import sys
from pathlib import Path

# Add project root to sys.path so we can run this script directly
sys.path.append(str(Path(__file__).parent.parent))

from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from corrective_rag.config import config

def get_llm() -> ChatGroq:
    """
    Initializes and returns a ChatGroq instance using llama-3.3-70b-versatile.
    """
    if not config.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable is not set. Please add it to your .env file.")
        
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=config.GROQ_API_KEY
    )

class Ping(BaseModel):
    """A trivial model to test structured output plumbing."""
    received: bool = Field(description="Whether the message was received.")
    echo: str = Field(description="The word to echo back.")

def run_warmup_test() -> Ping:
    """
    Tests the LLM connection and structured output capabilities.
    """
    llm = get_llm()
    structured_llm = llm.with_structured_output(Ping)
    
    prompt = "Respond with received=true and echo back the word 'pong'."
    print(f"Sending prompt: {repr(prompt)}")
    
    result = structured_llm.invoke(prompt)
    return result

if __name__ == "__main__":
    print("Testing Groq LLM connection and structured output...\n")
    
    try:
        ping_result = run_warmup_test()
        
        print("\n=== Warmup Test Result ===")
        print(f"Result Object: {ping_result}")
        print(f"Object Type:   {type(ping_result)}")
        
        if isinstance(ping_result, Ping):
            print("\nSuccess! The LLM successfully returned a true Pydantic instance.")
            print(f"Fields -> received: {ping_result.received}, echo: '{ping_result.echo}'")
        else:
            print("\nWarning: The output is not an instance of the Ping Pydantic model.")
            
    except Exception as e:
        print(f"\nError during testing. (Did you add your GROQ_API_KEY to the .env file?)\nDetails: {e}")
