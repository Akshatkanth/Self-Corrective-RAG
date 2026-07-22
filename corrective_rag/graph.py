import sys
from pathlib import Path
from typing import TypedDict

# Add project root to sys.path so we can run this script directly
sys.path.append(str(Path(__file__).parent.parent))

from langgraph.graph import StateGraph, END
from corrective_rag.ingest import Chunk
from corrective_rag.grader import GradeResult, grade_retrieval
from corrective_rag.rewrite import rewrite_query
from corrective_rag.vectorstore import load_index, retrieve
from corrective_rag.generate import generate_answer

# Load index globally so nodes (which are stateless functions) can access it
project_root = Path(__file__).parent.parent
index_directory = project_root / "faiss_index"

try:
    VECTOR_INDEX = load_index(str(index_directory))
except Exception:
    VECTOR_INDEX = None # Will handle in __main__

# 1. Define the Graph State
class GraphState(TypedDict):
    question: str
    current_query: str
    retrieved_chunks: list[Chunk]
    grade: GradeResult | None
    retry_count: int
    max_retries: int
    final_answer: str | None

# 2. Build the Nodes
def retrieve_node(state: GraphState) -> GraphState:
    print(f"\n---> [NODE: retrieve_node] Executing search...")
    print(f"     [Query] {repr(state['current_query'])}")
    
    chunks = retrieve(VECTOR_INDEX, state["current_query"], k=4)
    return {"retrieved_chunks": chunks}

def grade_node(state: GraphState) -> GraphState:
    print(f"\n---> [NODE: grade_node] Grading retrieval against ORIGINAL question...")
    print(f"     [Original Question] {repr(state['question'])}")
    
    grade = grade_retrieval(state["question"], state["retrieved_chunks"])
    print(f"     [Grade Result] Relevant: {grade.relevant}")
    print(f"     [Grade Reasoning] {grade.reasoning}")
    
    return {"grade": grade}

def rewrite_node(state: GraphState) -> GraphState:
    print(f"\n---> [NODE: rewrite_node] Reformulating query (Attempt {state['retry_count'] + 1} of {state['max_retries']})...")
    
    rewritten = rewrite_query(state["question"], state["grade"].reasoning)
    print(f"     [New Query] {repr(rewritten.query)}")
    print(f"     [Strategy] {rewritten.strategy}")
    
    return {
        "current_query": rewritten.query,
        "retry_count": state["retry_count"] + 1
    }

def not_found_node(state: GraphState) -> GraphState:
    print("\n---> [NODE: not_found_node] Exhausted all retries. Giving up.")
    return {"final_answer": "I couldn't find this in the docs."}

def answer_node(state: GraphState) -> GraphState:
    print("\n---> [NODE: answer_node] Relevant context found! Generating final answer...")
    
    result = generate_answer(state["question"], state["retrieved_chunks"])
    
    final_text = f"{result.answer}\n\nSources: {', '.join(result.sources)}"
    
    print(f"     [Generated Answer] {result.answer}")
    print(f"     [Sources Used] {result.sources}")
    
    return {"final_answer": final_text}

# 3. Define the Router Edge
def decide_next_step(state: GraphState) -> str:
    print(f"\n---> [ROUTER] Evaluating next step based on grade...")
    grade = state["grade"]
    
    if grade.relevant:
        print("     [Route] Relevant -> Routing to 'answer_node'")
        return "answer_node"
    
    if state["retry_count"] < state["max_retries"]:
        print("     [Route] Not Relevant (retries left) -> Routing to 'rewrite_node'")
        return "rewrite_node"
    
    print("     [Route] Not Relevant (retries exhausted) -> Routing to 'not_found_node'")
    return "not_found_node"

# 4. Wire the Graph together
workflow = StateGraph(GraphState)

workflow.add_node("retrieve_node", retrieve_node)
workflow.add_node("grade_node", grade_node)
workflow.add_node("rewrite_node", rewrite_node)
workflow.add_node("not_found_node", not_found_node)
workflow.add_node("answer_node", answer_node)

workflow.set_entry_point("retrieve_node")
workflow.add_edge("retrieve_node", "grade_node")

workflow.add_conditional_edges(
    "grade_node",
    decide_next_step,
    {
        "answer_node": "answer_node",
        "rewrite_node": "rewrite_node",
        "not_found_node": "not_found_node"
    }
)

workflow.add_edge("answer_node", END)
workflow.add_edge("not_found_node", END)
workflow.add_edge("rewrite_node", "retrieve_node")

# Compile into a runnable application
app = workflow.compile()

if __name__ == "__main__":
    if VECTOR_INDEX is None:
        print(f"Error: FAISS index not found at {index_directory}. Please run vectorstore.py first.")
        sys.exit(1)
        
    test_cases = [
        # a) Expect: 0 retries, hits answer_node
        "how do I roll back a deployment",
        
        # b) Expect: 2 retries exhausted, hits not_found_node
        "what's our uptime commitment to customers",
        
        # c) Expect: Succeeds on rewrite. 
        # "API keys" might return generic deployment stuff first, but should rewrite to 
        # "secrets rotation" and hit 07_secrets_rotation.md on a subsequent attempt.
        "how to safely change API keys without breaking production"
    ]
    
    for idx, question in enumerate(test_cases):
        print("\n" + "="*80)
        print(f"TEST CASE {idx+1}: {repr(question)}")
        print("="*80)
        
        initial_state = {
            "question": question,
            "current_query": question,
            "retrieved_chunks": [],
            "grade": None,
            "retry_count": 0,
            "max_retries": 2,
            "final_answer": None
        }
        
        # Run the graph
        final_state = app.invoke(initial_state)
        
        print("\n" + "-"*50)
        print("FINAL STATE SUMMARY:")
        print(f"Original Question: {repr(final_state['question'])}")
        print(f"Final Query Used:  {repr(final_state['current_query'])}")
        print(f"Retry Count:       {final_state['retry_count']} / {final_state['max_retries']}")
        print(f"Final Answer:      {final_state['final_answer']}")
        print("-"*50 + "\n")
