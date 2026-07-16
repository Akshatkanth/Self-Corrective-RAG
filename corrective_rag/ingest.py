import os
from pathlib import Path
from dataclasses import dataclass
from langchain_text_splitters import RecursiveCharacterTextSplitter

@dataclass
class Chunk:
    text: str
    source_file: str
    chunk_index: int

def load_and_chunk_docs(docs_dir: str) -> list[Chunk]:
    """
    Reads all .md files from docs_dir and splits them into chunks.
    
    Args:
        docs_dir (str): Path to the directory containing markdown documents.
        
    Returns:
        list[Chunk]: A list of Chunk objects containing text, source filename, and index.
    """
    chunks = []
    docs_path = Path(docs_dir)
    
    # Initialize the LangChain RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    
    # Read all .md files in the directory
    for filepath in docs_path.glob("*.md"):
        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            continue
            
        # Split the document text into string chunks
        text_chunks = splitter.split_text(content)
        
        # Create Chunk objects preserving metadata
        for idx, text in enumerate(text_chunks):
            chunk = Chunk(
                text=text,
                source_file=filepath.name,
                chunk_index=idx
            )
            chunks.append(chunk)
            
    return chunks

if __name__ == "__main__":
    # Ensure this runs correctly when invoked directly
    # Assuming the docs directory is at the project root
    project_root = Path(__file__).parent.parent
    docs_directory = project_root / "docs"
    
    print(f"Loading and chunking documents from: {docs_directory}")
    
    all_chunks = load_and_chunk_docs(str(docs_directory))
    
    print(f"\nTotal chunks created: {len(all_chunks)}")
    print("-" * 40)
    
    if not all_chunks:
        print("No chunks found. Make sure there are .md files in the docs directory.")
    else:
        print("First 3 chunks:\n")
        for i, chunk in enumerate(all_chunks[:3]):
            print(f"Chunk {i+1} from {chunk.source_file} (Index: {chunk.chunk_index}):")
            print(repr(chunk.text))
            print("-" * 40)
