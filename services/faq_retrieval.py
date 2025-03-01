from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings  # Free alternative
from langchain.schema import Document
import json
import os

def load_faq_db(faq_file: str = "data/faqs.json"):
    if not os.path.exists(faq_file):
        raise FileNotFoundError(f"FAQ file not found: {faq_file}")
    with open(faq_file, "r") as f:
        faq_list = json.load(f)
    documents = [
        Document(page_content=f"Q: {faq['question']} A: {faq['answer']}")
        for faq in faq_list
    ]
    # Use a free HuggingFace model for embeddings; no API key needed.
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.from_documents(documents, embedding_model)

faq_db = load_faq_db()

def get_faq_answer(query: str) -> str:
    results = faq_db.similarity_search(query)
    return results[0].page_content if results else "I'm sorry, I don't have an answer for that."
