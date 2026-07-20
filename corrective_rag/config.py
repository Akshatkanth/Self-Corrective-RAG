import os
import warnings
from dotenv import load_dotenv

# Suppress LangChain's Pydantic V1 warning
warnings.filterwarnings("ignore", category=UserWarning, message=".*Core Pydantic V1 functionality.*")

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the Corrective RAG system."""
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

config = Config()
