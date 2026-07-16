import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the Corrective RAG system."""
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

config = Config()
