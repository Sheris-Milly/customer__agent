# config.py
import os

# Model settings
MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# API Settings
API_HOST = "0.0.0.0"
API_PORT = 8000

# Paths
FAQ_PATH = os.path.join(os.path.dirname(__file__), "data/faqs.json")

# Model parameters
MAX_LENGTH = 512
TEMPERATURE = 0.7