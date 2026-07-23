import sys
import argparse
import os
from contextlib import redirect_stdout

from corrective_rag.graph import app, VECTOR_INDEX

def run_query(question: str, verbose: bool):
    if VECTOR_INDEX is None:
        print("Error: FAISS index not found. Please run 'python corrective_rag/vectorstore.py' first.")
        sys.exit(1)
        
    initial_state = {
        "question": question,
        "current_query": question,
        "retrieved_chunks": [],
        "grade": None,
        "retry_count": 0,
        "max_retries": 2,
        "final_answer": None
    }
    
    if not verbose:
        # Suppress the internal node debugging prints to keep the CLI clean
        with open(os.devnull, 'w') as f, redirect_stdout(f):
            final_state = app.invoke(initial_state)
    else:
        final_state = app.invoke(initial_state)
        
    # Output the final result
    if verbose:
        print("\n" + "="*80)
        print("FINAL RESULT")
        print("="*80)
        
    print(final_state["final_answer"])
    
    if verbose:
        print("="*80 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Corrective RAG CLI - Ask questions about your documentation.")
    parser.add_argument("question", type=str, help="The question you want to ask the docs.")
    parser.add_argument("--verbose", action="store_true", help="Show the node-by-node execution trace (retrieve -> grade -> rewrite -> answer).")
    
    args = parser.parse_args()
    
    run_query(args.question, args.verbose)
