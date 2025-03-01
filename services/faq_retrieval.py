# services/faq_retrieval.py
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
import json
import os
import logging
from config import EMBEDDING_MODEL, FAQ_PATH

logger = logging.getLogger(__name__)


def load_faq_db(faq_file=FAQ_PATH):
    """
    Load FAQs from JSON and create a vector store with embeddings.
    """
    try:
        if not os.path.exists(faq_file):
            logger.error(f"FAQ file not found: {faq_file}")
            # Create an empty vector store with the embedding model
            embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
            return FAISS.from_texts(["No FAQs available"], embedding_model)

        with open(faq_file, "r") as f:
            faq_list = json.load(f)

        logger.info(f"Loaded {len(faq_list)} FAQs from {faq_file}")

        # Create documents from FAQs
        documents = [
            Document(page_content=f"Q: {faq['question']} A: {faq['answer']}")
            for faq in faq_list
        ]

        # Use HuggingFace embeddings (free, no API key needed)
        embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

        # Create and return the vector store
        vector_store = FAISS.from_documents(documents, embedding_model)
        logger.info("FAQ vector store created successfully")
        return vector_store

    except Exception as e:
        logger.error(f"Error loading FAQ database: {str(e)}")
        # Return an empty vector store
        embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        return FAISS.from_texts(["Error loading FAQs"], embedding_model)


# Initialize the FAQ database
try:
    faq_db = load_faq_db()
except Exception as e:
    logger.error(f"Failed to initialize FAQ database: {str(e)}")
    # Create empty database for testing
    embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    faq_db = FAISS.from_texts(["FAQ system unavailable"], embedding_model)


def get_faq_answer(query: str) -> str:
    """
    Search for similar questions in the FAQ database and return the answer.
    """
    try:
        results = faq_db.similarity_search(query, k=1)
        if results:
            return results[0].page_content
        return "I couldn't find a relevant answer in our FAQ database."
    except Exception as e:
        logger.error(f"Error retrieving FAQ answer: {str(e)}")
        return "Sorry, the FAQ system is currently unavailable."