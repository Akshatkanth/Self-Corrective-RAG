import os
import sys
from pathlib import Path

# Add project root to sys.path so we can run this script directly
sys.path.append(str(Path(__file__).parent.parent))

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from corrective_rag.ingest import Chunk, load_and_chunk_docs

def get_embeddings_model():
    """
    Returns the HuggingFace embeddings model.
    'all-MiniLM-L6-v2' is a fast, local model that doesn't require an API key.
    """
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def build_index(chunks: list[Chunk]) -> FAISS:
    """
    Embeds all chunks and builds a FAISS index.
    
    Args:
        chunks (list[Chunk]): List of Chunk objects containing text and metadata.
        
    Returns:
        FAISS: The built FAISS vector store index.
    """
    embeddings = get_embeddings_model()
    
    # Extract texts and metadatas for LangChain's FAISS integration
    texts = [chunk.text for chunk in chunks]
    metadatas = [
        {
            "source_file": chunk.source_file,
            "chunk_index": chunk.chunk_index
        }
        for chunk in chunks
    ]
    
    # Build FAISS index from texts and metadatas
    index = FAISS.from_texts(texts=texts, embedding=embeddings, metadatas=metadatas)
    return index

def save_index(index: FAISS, index_path: str):
    """
    Persist the FAISS index to disk.
    """
    index.save_local(index_path)

def load_index(index_path: str) -> FAISS:
    """
    Load a FAISS index from disk.
    """
    embeddings = get_embeddings_model()
    # allow_dangerous_deserialization=True is required for loading pickle files safely
    # since we are loading our own generated index locally, it is safe.
    return FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)

def retrieve(index: FAISS, query: str, k: int = 4) -> list[Chunk]:
    """
    Embeds the query and returns the top-k most similar chunks.
    
    Args:
        index (FAISS): The FAISS index.
        query (str): The search query.
        k (int): Number of top results to return.
        
    Returns:
        list[Chunk]: A list of retrieved Chunk objects mapped back from FAISS Documents.
    """
    # similarity_search returns LangChain Document objects
    docs = index.similarity_search(query, k=k)
    
    # Convert back to our custom Chunk format to retain standard metadata
    retrieved_chunks = []
    for doc in docs:
        chunk = Chunk(
            text=doc.page_content,
            source_file=doc.metadata.get("source_file", "unknown"),
            chunk_index=doc.metadata.get("chunk_index", -1)
        )
        retrieved_chunks.append(chunk)
        
    return retrieved_chunks

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    docs_directory = project_root / "docs"
    index_directory = project_root / "faiss_index"
    
    # 1. Build or Load the Index
    if index_directory.exists() and (index_directory / "index.faiss").exists():
        print(f"Loading existing FAISS index from {index_directory}...")
        vector_index = load_index(str(index_directory))
    else:
        print("FAISS index not found. Building new index...")
        all_chunks = load_and_chunk_docs(str(docs_directory))
        
        if not all_chunks:
            print("No chunks found to index. Exiting.")
            exit(1)
            
        print(f"Embedding {len(all_chunks)} chunks and building index (this may take a moment to download the model on the first run)...")
        vector_index = build_index(all_chunks)
        
        print(f"Saving index to {index_directory}...")
        save_index(vector_index, str(index_directory))
        
    # 2. Test Retrieval
    print("\n" + "="*50)
    print("TESTING RETRIEVAL")
    print("="*50)
    
    test_queries = [
        "how do I roll back a deployment",
        "what is our database backup schedule"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {repr(query)}")
        print("-" * 30)
        # We can use k=2 or k=4 depending on how much we want to see
        results = retrieve(vector_index, query, k=3)
        
        for i, res in enumerate(results):
            print(f"Result {i+1} [Source: {res.source_file}, Index: {res.chunk_index}]:")
            # Print a snippet of the text (first 150 chars)
            snippet = res.text if len(res.text) < 150 else res.text[:147] + "..."
            print(f"Text: {repr(snippet)}")
            print("-" * 15)
