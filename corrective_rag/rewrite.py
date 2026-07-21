import sys
from pathlib import Path

# Add project root to sys.path so we can run this script directly
sys.path.append(str(Path(__file__).parent.parent))

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from corrective_rag.llm import get_llm
from corrective_rag.vectorstore import load_index, retrieve
from corrective_rag.grader import grade_retrieval

class RewrittenQuery(BaseModel):
    """Result of reformulating a search query."""
    query: str = Field(
        description="The reformulated search query, optimized for vector search embedding."
    )
    strategy: str = Field(
        description="Brief note on what changed and why (e.g., 'used more specific technical terms')."
    )

def rewrite_query(original_question: str, grade_reasoning: str) -> RewrittenQuery:
    """
    Reformulates a query optimized for vector search, based on the failure reasoning.
    """
    llm = get_llm()
    structured_llm = llm.with_structured_output(RewrittenQuery)
    
    system_prompt = """You are an expert at optimizing search queries for vector database retrieval.

The user asked a question, but our initial search retrieved irrelevant context. 
We need to try again with a better search query.

Original Question: {original_question}
Failure Reasoning (Why the first search failed): {grade_reasoning}

TASK:
Produce a new search query optimized for vector similarity search.
Do NOT simply rephrase the question for a human. Instead, use different keywords, 
more/less specific terminology, or frame the underlying need differently so it 
embeds closer to the right source documents.
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Rewrite the query to improve retrieval.")
    ])
    
    chain = prompt | structured_llm
    
    result = chain.invoke({
        "original_question": original_question,
        "grade_reasoning": grade_reasoning
    })
    
    return result

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    index_directory = project_root / "faiss_index"
    
    if not index_directory.exists() or not (index_directory / "index.faiss").exists():
        print(f"Error: FAISS index not found at {index_directory}. Please run vectorstore.py first.")
        sys.exit(1)
        
    print("Loading FAISS index...")
    vector_index = load_index(str(index_directory))
    
    test_question = "what's our uptime commitment to customers"
    
    print("\n" + "="*50)
    print("TESTING RETRIEVAL -> GRADE -> REWRITE CHAIN")
    print("="*50)
    
    # 1. Initial Retrieval
    print(f"\n[1] Initial Query: {repr(test_question)}")
    initial_chunks = retrieve(vector_index, test_question, k=4)
    print(f"    Retrieved {len(initial_chunks)} chunks.")
    
    # 2. Initial Grade
    print("\n[2] Grading Initial Retrieval...")
    initial_grade = grade_retrieval(test_question, initial_chunks)
    print(f"    Relevant:  {initial_grade.relevant}")
    print(f"    Reasoning: {initial_grade.reasoning}")
    
    if initial_grade.relevant:
        print("\nSurprisingly, the grader found relevant context! Stopping here.")
    else:
        # 3. Rewrite Query
        print("\n[3] Rewriting Query based on failure reasoning...")
        rewritten = rewrite_query(test_question, initial_grade.reasoning)
        print(f"    New Query: {repr(rewritten.query)}")
        print(f"    Strategy:  {rewritten.strategy}")
        
        # 4. New Retrieval
        print("\n[4] Second Retrieval Attempt...")
        new_chunks = retrieve(vector_index, rewritten.query, k=4)
        print(f"    Retrieved {len(new_chunks)} chunks.")
        
        # 5. New Grade
        print("\n[5] Grading Second Retrieval...")
        new_grade = grade_retrieval(test_question, new_chunks)
        print(f"    Relevant:  {new_grade.relevant}")
        print(f"    Reasoning: {new_grade.reasoning}")
        
    print("\n" + "="*50)
