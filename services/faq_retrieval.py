import json
import logging
import os
import numpy as np
from typing import List, Dict, Tuple, Optional

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document

from config import FAQ_PATH, EMBEDDING_MODEL

# Configure logging
logger = logging.getLogger(__name__)


class FAQRetrieval:
    """
    A service for retrieving FAQs based on vector similarity search.
    """

    def __init__(self):
        """Initialize the FAQ retrieval service."""
        logger.info("Initializing FAQ retrieval service")

        try:
            # Load the embedding model
            self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
            logger.debug(f"Loaded embedding model: {EMBEDDING_MODEL}")

            # Create or load the FAQ data
            self.create_or_load_faq_data()

            # Initialize the vector store
            self.initialize_vector_store()

        except Exception as e:
            logger.error(f"Error initializing FAQ retrieval service: {str(e)}")
            raise RuntimeError(f"Failed to initialize FAQ retrieval service: {str(e)}")

    def create_or_load_faq_data(self):
        """Create FAQ data file if it doesn't exist, or load existing data."""
        try:
            if not os.path.exists(FAQ_PATH):
                logger.info(f"FAQ data file not found. Creating default FAQ data at {FAQ_PATH}")

                # Create a default set of FAQs
                default_faqs = [
                    {
                        "question": "How do I track my order?",
                        "answer": "You can track your order by entering your order ID in the order tracking section on our website or by contacting our customer support."
                    },
                    {
                        "question": "What is your return policy?",
                        "answer": "We accept returns within 30 days of purchase. Items must be in their original condition with tags attached. Please visit our Returns page for more details."
                    },
                    {
                        "question": "How long does shipping take?",
                        "answer": "Standard shipping typically takes 3-5 business days within the continental US. Express shipping options are available for 1-2 day delivery."
                    },
                    {
                        "question": "Do you ship internationally?",
                        "answer": "Yes, we ship to most countries worldwide. International shipping times vary by destination, typically taking 7-14 business days."
                    },
                    {
                        "question": "How can I change or cancel my order?",
                        "answer": "You can change or cancel your order within 1 hour of placing it. Please contact our customer service team immediately with your order number."
                    },
                    {
                        "question": "What payment methods do you accept?",
                        "answer": "We accept Visa, Mastercard, American Express, PayPal, and Apple Pay."
                    },
                    {
                        "question": "Are my payment details secure?",
                        "answer": "Yes, we use industry-standard encryption and security measures to protect your payment information."
                    },
                    {
                        "question": "How do I create an account?",
                        "answer": "You can create an account by clicking on the 'Sign Up' button at the top of our website and following the registration process."
                    }
                ]

                # Save the default FAQs
                os.makedirs(os.path.dirname(FAQ_PATH), exist_ok=True)
                with open(FAQ_PATH, 'w') as f:
                    json.dump(default_faqs, f, indent=2)

                self.faqs = default_faqs
            else:
                # Load existing FAQs
                logger.debug(f"Loading existing FAQ data from {FAQ_PATH}")
                with open(FAQ_PATH, 'r') as f:
                    self.faqs = json.load(f)

                logger.info(f"Loaded {len(self.faqs)} FAQs")

        except Exception as e:
            logger.error(f"Error creating or loading FAQ data: {str(e)}")
            raise RuntimeError(f"Failed to create or load FAQ data: {str(e)}")

    def initialize_vector_store(self):
        """Initialize the FAISS vector store with FAQ data."""
        try:
            logger.debug("Initializing FAISS vector store")

            # Convert FAQs to documents for the vector store
            documents = []
            metadatas = []

            for i, faq in enumerate(self.faqs):
                documents.append(faq["question"])
                metadatas.append({"index": i, "question": faq["question"], "answer": faq["answer"]})

            # Create the vector store
            self.vector_store = FAISS.from_texts(
                texts=documents,
                embedding=self.embeddings,
                metadatas=metadatas
            )

            logger.info(f"Initialized vector store with {len(documents)} FAQ documents")

        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise RuntimeError(f"Failed to initialize vector store: {str(e)}")

    def retrieve_relevant_faqs(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve the most relevant FAQs for a given query.

        Args:
            query: The user's question or query
            top_k: The number of top results to return

        Returns:
            A list of the most relevant FAQ entries
        """
        try:
            logger.debug(f"Retrieving FAQs for query: {query}")

            # Search for similar questions
            results = self.vector_store.similarity_search_with_score(query, k=top_k)

            # Extract and format results
            relevant_faqs = []
            for doc, score in results:
                # Convert the score to a similarity percentage (FAISS returns L2 distance, smaller is better)
                # Convert to similarity where 1.0 is perfect match
                similarity = 1.0 / (1.0 + score)

                relevant_faqs.append({
                    "question": doc.metadata["question"],
                    "answer": doc.metadata["answer"],
                    "similarity": similarity
                })

            logger.debug(f"Retrieved {len(relevant_faqs)} relevant FAQs")
            return relevant_faqs

        except Exception as e:
            logger.error(f"Error retrieving relevant FAQs: {str(e)}")
            return []

    def get_all_faqs(self) -> List[Dict]:
        """
        Get all available FAQs.

        Returns:
            A list of all FAQ entries
        """
        return self.faqs

    def is_faq_question(self, query: str, threshold: float = 0.75) -> Tuple[bool, Optional[Dict]]:
        """
        Determine if a query is closely matching an FAQ question.

        Args:
            query: The user's question or query
            threshold: The similarity threshold to consider a match

        Returns:
            A tuple of (is_faq, faq_entry)
        """
        try:
            # Get the most relevant FAQ
            relevant_faqs = self.retrieve_relevant_faqs(query, top_k=1)

            if relevant_faqs and relevant_faqs[0]["similarity"] >= threshold:
                logger.debug(f"Query matches FAQ with similarity {relevant_faqs[0]['similarity']}")
                return True, relevant_faqs[0]

            logger.debug("Query does not closely match any FAQ")
            return False, None

        except Exception as e:
            logger.error(f"Error checking if query is an FAQ: {str(e)}")
            return False, None