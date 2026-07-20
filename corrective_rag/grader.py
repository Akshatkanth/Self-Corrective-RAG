import sys
from pathlib import Path

# Add project root to sys.path so we can run this script directly
sys.path.append(str(Path(__file__).parent.parent))

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from corrective_rag.llm import get_llm
from corrective_rag.ingest import Chunk
from corrective_rag.vectorstore import load_index, retrieve

class GradeResult(BaseModel):
    """Result of grading the relevance of retrieved context."""
    relevant: bool = Field(
        description="Whether the retrieved chunks contain enough information to actually answer the question."
    )
    reasoning: str = Field(
        description="Brief explanation of why the context is or isn't relevant. Be specific about what is missing if irrelevant."
    )

def grade_retrieval(question: str, chunks: list[Chunk]) -> GradeResult:
    """
    Grades the relevance of retrieved chunks against the user's question.
    """
    llm = get_llm()
    structured_llm = llm.with_structured_output(GradeResult)
    
    # Format chunks into a single context block with source filenames
    context_parts = []
    for chunk in chunks:
        context_parts.append(f"--- SOURCE: {chunk.source_file} ---\n{chunk.text}\n")
    
    formatted_context = "\n".join(context_parts)
    
    # Define a strict grading prompt
    system_prompt = """You are a strict evaluator grading the relevance of retrieved context for answering a user's question.

Given the context provided below, can you fully and specifically answer the user's question? 

RULES FOR GRADING:
- Answer 'no' (relevant=false) if the context is only tangentially related.
- Answer 'no' (relevant=false) if the context covers a different topic.
- Answer 'no' (relevant=false) if you would have to guess or use outside knowledge to fill gaps.
- Partial or tangential relevance should be graded as NOT relevant. We want a strict grader.
- Provide a brief, specific reasoning for your decision (e.g., "chunks discuss deployment rollback but not database backup schedules").

CONTEXT:
{context}
"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Question: {question}")
    ])
    
    chain = prompt | structured_llm
    
    result = chain.invoke({
        "context": formatted_context,
        "question": question
    })
    
    return result

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    index_directory = project_root / "faiss_index"
    
    if not index_directory.exists() or not (index_directory / "index.faiss").exists():
        print(f"Error: FAISS index not found at {index_directory}. Please run vectorstore.py first to build it.")
        sys.exit(1)
        
    print("Loading FAISS index...")
    vector_index = load_index(str(index_directory))
    
    test_cases = [
        "how do I roll back a deployment",
        "what is our database backup schedule",
        "what are the SEV1 incident response time requirements"
    ]
    
    print("\n" + "="*50)
    print("TESTING STRICT RETRIEVAL GRADER")
    print("="*50)
    
    for question in test_cases:
        print(f"\nQuestion: {repr(question)}")
        
        # Retrieve top 4 chunks
        retrieved_chunks = retrieve(vector_index, question, k=4)
        
        if not retrieved_chunks:
            print("No chunks retrieved.")
            continue
            
        print(f"Retrieved {len(retrieved_chunks)} chunks. Grading...")
        
        # Grade the retrieved chunks
        grade = grade_retrieval(question, retrieved_chunks)
        
        # Print results
        print(f"Relevant:  {grade.relevant}")
        print(f"Reasoning: {grade.reasoning}")
        print("-" * 50)
