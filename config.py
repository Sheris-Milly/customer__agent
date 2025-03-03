import os

# Model settings
MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Model parameters
MAX_LENGTH = 512
TEMPERATURE = 0.7

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FAQ_PATH = os.path.join(DATA_DIR, "faqs.json")
ORDER_DATA_PATH = os.path.join(DATA_DIR, "orders.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)