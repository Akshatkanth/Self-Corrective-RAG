import sys
from pathlib import Path

# Add project root to sys.path so we can run this script directly
sys.path.append(str(Path(__file__).parent.parent))

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from corrective_rag.llm import get_llm
from corrective_rag.ingest import Chunk

class AnswerResult(BaseModel):
    """Result of generating an answer from context."""
    answer: str = Field(
        description="The actual answer to the user's question based on the provided context."
    )
    sources: list[str] = Field(
        description="List of filenames of the chunks actually used to support the answer. Do not include files that weren't used."
    )

def generate_answer(question: str, chunks: list[Chunk]) -> AnswerResult:
    """
    Generates an answer using the LLM based ONLY on the provided chunks, 
    including citations back to the source filenames.
    """
    llm = get_llm()
    structured_llm = llm.with_structured_output(AnswerResult)
    
    context_parts = []
    for chunk in chunks:
        context_parts.append(f"--- SOURCE: {chunk.source_file} ---\n{chunk.text}\n")
    
    formatted_context = "\n".join(context_parts)
    
    system_prompt = """You are a helpful and precise assistant.

Your task is to answer the user's question using ONLY the provided context below. 

RULES:
- Base your answer ONLY on the provided context.
- If the context doesn't fully support part of the answer, DO NOT fill the gap with general knowledge. Explicitly state what is missing instead.
- List which source filenames you actually drew from in the `sources` field. Do not list sources that you did not use.

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
