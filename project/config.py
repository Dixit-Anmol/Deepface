import os
from dotenv import load_dotenv

# Project root directory configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(BASE_DIR, "data")
VECTORSTORE_DIR = os.path.join(BASE_DIR, "vectorstore")

# Load environment variables from the repository root .env file
dotenv_path = os.path.join(ROOT_DIR, ".env")
load_dotenv(dotenv_path)

# File paths
PDF_PATH = os.path.join(DATA_DIR, "final_geeta.pdf")
FAISS_INDEX_PATH = os.path.join(VECTORSTORE_DIR, "faiss.index")
METADATA_PATH = os.path.join(VECTORSTORE_DIR, "metadata.pkl")

# Model Configuration
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Groq LLM Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

# Text Processing & Retrieval Hyperparameters
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
TOP_K = 5
