import logging
import re
from typing import Dict, List, Tuple, Optional, Any

from models.deepseek_model import DeepSeekModel
from services.faq_retrieval import FAQRetrieval
from services.memory import ConversationMemory
from services.order_tracking import OrderTrackingService

# Configure logging
logger = logging.getLogger(__name__)


class ChatbotAgent:
    """
    Main chatbot agent that integrates various services to provide intelligent responses.
    """

    def __init__(self):
        """Initialize the chatbot agent and its dependencies."""
        logger.info("Initializing chatbot agent")

        try:
            # Initialize services
            self.model = DeepSeekModel()
            logger.debug("Initialized DeepSeek model")

            self.faq_service = FAQRetrieval()
            logger.debug("Initialized FAQ retrieval service")

            self.memory = ConversationMemory()
            logger.debug("Initialized conversation memory service")

            self.order_service = OrderTrackingService()
            logger.debug("Initialized order tracking service")

            # Define system prompt for the model
            self.system_prompt = """
            You are a helpful customer service assistant for an e-commerce store.
            Your goal is to provide accurate, friendly, and helpful responses to customer inquiries.
            Answer directly without revealing any internal chain-of-thought or reasoning process.
            Keep your responses concise, friendly, and professional.
            """

            logger.info("Chatbot agent initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing chatbot agent: {str(e)}")
            raise RuntimeError(f"Failed to initialize chatbot agent: {str(e)}")

    def process_message(
            self,
            message: str,
            session_id: str,
            context: Optional[Dict] = None
    ) -> Tuple[str, Dict]:
        """
        Process a user message and generate a response.

        Args:
            message: The user's message
            session_id: The unique identifier for the conversation session
            context: Additional context information

        Returns:
            A tuple of (response, updated_context)
        """
        try:
            logger.debug(f"Processing message for session {session_id}: {message}")

            # Update context if provided
            if context:
                self.memory.update_context(session_id, context)

            # Get current context
            current_context = self.memory.get_context(session_id)

            # Add user message to memory
            self.memory.add_message(session_id, "user", message)

            # Check if message contains an order tracking request
            order_id = self._extract_order_id(message)
            if order_id:
                logger.debug(f"Detected order tracking request for order ID: {order_id}")
                response = self._handle_order_tracking(order_id)

                # Update context with order information
                order_info = self.order_service.get_order(order_id)
                if order_info:
                    self.memory.update_context(session_id, {"last_tracked_order": order_info})

            # Check if message is an FAQ
            elif self._is_faq_question(message):
                logger.debug("Detected FAQ question")
                response = self._handle_faq_question(message)

            # Otherwise, use the language model for a response
            else:
                logger.debug("Using language model for response")
                response = self._generate_model_response(message, session_id)

            # Add assistant response to memory
            self.memory.add_message(session_id, "assistant", response)

            # Get updated context
            updated_context = self.memory.get_context(session_id)

            logger.debug(f"Generated response for session {session_id}: {response[:50]}...")
            return response, updated_context

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return f"I'm sorry, I encountered an error while processing your request. Please try again later or contact our support team. (Error: {str(e)})", {}

    def _extract_order_id(self, message: str) -> Optional[str]:
        """Extract order ID from the message if present."""
        try:
            # Common order ID patterns
            patterns = [
                r"order\s*#?\s*([A-Za-z0-9\-]+)",
                r"tracking\s*.*\s*order\s*#?\s*([A-Za-z0-9\-]+)",
                r"#\s*([A-Za-z0-9\-]+)",
                r"ORD-\d+"
            ]

            # Try each pattern
            for pattern in patterns:
                matches = re.search(pattern, message, re.IGNORECASE)
                if matches:
                    order_id = matches.group(1) if len(matches.groups()) > 0 else matches.group(0)

                    # Validate that this looks like an order ID
                    if re.match(r"^ORD-\d+$", order_id, re.IGNORECASE) or re.match(r"^[A-Za-z0-9\-]{6,}$", order_id):
                        logger.debug(f"Extracted order ID: {order_id}")
                        return order_id

            # Check if message contains tracking keywords and is short (likely just an order number)
            tracking_keywords = ["track", "order", "status", "where", "package"]
            if any(keyword in message.lower() for keyword in tracking_keywords) and len(message.split()) < 10:
                # Try to extract any alphanumeric sequence that could be an order ID
                matches = re.search(r"([A-Za-z0-9\-]{6,})", message)
                if matches:
                    logger.debug(f"Extracted potential order ID from short message: {matches.group(1)}")
                    return matches.group(1)

            logger.debug("No order ID found in message")
            return None

        except Exception as e:
            logger.error(f"Error extracting order ID: {str(e)}")
            return None

    def _handle_order_tracking(self, order_id: str) -> str:
        """Generate a response for an order tracking request."""
        try:
            logger.debug(f"Handling order tracking for: {order_id}")

            # Get order information
            order_info = self.order_service.get_order(order_id)

            if not order_info:
                return f"I couldn't find an order with the ID {order_id}. Please check that you've entered the correct order number and try again."

            # Generate response based on order status
            status = order_info["status"]

            if status == "Processing":
                return f"Your order #{order_id} is currently being processed. It was placed on {order_info['order_date']} and should ship soon. You'll receive an email with tracking information once it ships."

            elif status == "Confirmed":
                return f"Your order #{order_id} has been confirmed and is being prepared for shipping. It was placed on {order_info['order_date']}. We'll send you a tracking number once it ships."

            elif status == "Shipped":
                tracking = order_info.get("tracking_number", "Not available")
                ship_date = order_info.get("shipping_date", "recently")
                delivery = order_info.get("delivery_date", "soon")

                return f"Good news! Your order #{order_id} has shipped on {ship_date}. Your tracking number is {tracking}. The estimated delivery date is {delivery}."

            elif status == "In Transit":
                tracking = order_info.get("tracking_number", "Not available")
                delivery = order_info.get("delivery_date", "soon")

                return f"Your order #{order_id} is currently in transit. Your tracking number is {tracking}. The estimated delivery date is {delivery}. You can track your package using the tracking number on our website or the carrier's site."

            elif status == "Delivered":
                delivery = order_info.get("delivery_date", "recently")

                return f"Your order #{order_id} has been delivered on {delivery}. If you haven't received it or have any issues with your order, please let me know and I'll be happy to help."

            else:
                return f"Your order #{order_id} is currently marked as '{status}'. If you have any questions or concerns about your order, please let me know."

        except Exception as e:
            logger.error(f"Error handling order tracking: {str(e)}")
            return "I'm having trouble retrieving your order information at the moment. Please try again later or contact our customer support team for assistance."

    def _is_faq_question(self, message: str) -> bool:
        """Determine if the message is an FAQ question."""
        try:
            is_faq, _ = self.faq_service.is_faq_question(message)
            return is_faq

        except Exception as e:
            logger.error(f"Error checking if message is FAQ: {str(e)}")
            return False

    def _handle_faq_question(self, message: str) -> str:
        """Generate a response for an FAQ question."""
        try:
            logger.debug("Handling FAQ question")

            is_faq, faq_entry = self.faq_service.is_faq_question(message)

            if is_faq and faq_entry:
                logger.debug(f"Found matching FAQ: {faq_entry['question']}")
                return faq_entry["answer"]

            # Fall back to retrieving relevant FAQs
            relevant_faqs = self.faq_service.retrieve_relevant_faqs(message, top_k=1)

            if relevant_faqs:
                logger.debug(f"Using most relevant FAQ: {relevant_faqs[0]['question']}")
                return relevant_faqs[0]["answer"]

            logger.debug("No relevant FAQ found, falling back to model")
            return self._generate_model_response(message, "default")

        except Exception as e:
            logger.error(f"Error handling FAQ question: {str(e)}")
            return "I'm having trouble finding information about that right now. Let me help you with something else or connect you with a support agent."

    def _generate_model_response(self, message: str, session_id: str) -> str:
        """Generate a response using the language model."""
        try:
            logger.debug("Generating model response")

            # Get conversation history
            history = self.memory.get_conversation_history(session_id, max_messages=5)

            # Generate response
            response = self.model.generate_response(
                prompt=message,
                system_prompt=self.system_prompt,
                context=history
            )

            logger.debug(f"Model generated response: {response[:50]}...")
            return response

        except Exception as e:
            logger.error(f"Error generating model response: {str(e)}")
            return "I'm having trouble generating a response right now. Please try again or ask me something else."

    def track_order(self, order_id: str) -> Dict:
        """
        Track an order by ID.

        Args:
            order_id: The ID of the order to track

        Returns:
            Order information dictionary
        """
        try:
            logger.debug(f"Tracking order: {order_id}")

            order_info = self.order_service.get_order(order_id)

            if not order_info:
                logger.debug(f"Order not found: {order_id}")
                return {"error": f"Order {order_id} not found"}

            logger.debug(f"Found order {order_id} with status {order_info['status']}")
            return order_info

        except Exception as e:
            logger.error(f"Error tracking order {order_id}: {str(e)}")
            return {"error": f"Failed to track order: {str(e)}"}

    def get_faqs(self) -> List[Dict]:
        """
        Get all available FAQs.

        Returns:
            A list of FAQ dictionaries
        """
        try:
            logger.debug("Retrieving all FAQs")
            return self.faq_service.get_all_faqs()

        except Exception as e:
            logger.error(f"Error retrieving FAQs: {str(e)}")
            return []

    def reset_conversation(self, session_id: str) -> None:
        """
        Reset the conversation for a session.

        Args:
            session_id: The unique identifier for the conversation session
        """
        try:
            logger.debug(f"Resetting conversation for session {session_id}")
            self.memory.reset_session(session_id)

        except Exception as e:
            logger.error(f"Error resetting conversation for session {session_id}: {str(e)}")
            raise RuntimeError(f"Failed to reset conversation: {str(e)}")