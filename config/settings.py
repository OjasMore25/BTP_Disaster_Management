"""
Configuration settings for Disaster Response RAG System
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")
GROQ_MODEL = "qwen/qwen3-32b"  # Active model (llama-3.1-70b-versatile was decommissioned)

# Database Configuration
DATABASE_PATH = "database/demo_data"
SHELTER_DATA_FILE = "database/shelters_mumbai.json"
OPERATIONS_DATA_FILE = "database/rescue_operations_mumbai.json"

# Vector/Embedding Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# RAG Configuration
TOP_K_RESULTS = 5
CONFIDENCE_THRESHOLD = 0.6
TEMPERATURE = 0.7

# Mumbai Coordinates for context
MUMBAI_CENTER_LAT = 19.0760
MUMBAI_CENTER_LON = 72.8777
MUMBAI_BOUNDS = {
    "min_lat": 18.90,
    "max_lat": 19.25,
    "min_lon": 72.70,
    "max_lon": 73.05
}

# Message Types
MESSAGE_TYPE_VICTIM = "victim"
MESSAGE_TYPE_RESCUER = "rescuer"

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "logs/disaster_rag.log"
