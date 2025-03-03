import logging
from typing import Dict, List, Optional, Any

# Configure logging
logger = logging.getLogger(__name__)


class ConversationMemory:
    """
    A service for managing conversation history and context for chat sessions.
    """

    def __init__(self):
        """Initialize the conversation memory service."""
        logger.info("Initializing conversation memory service")

        # Dictionary to store conversation history for each session
        self.conversations = {}

        # Dictionary to store user context for each session
        self.contexts = {}

        logger.debug("Conversation memory service initialized")

    def add_message(
            self,
            session_id: str,
            role: str,
            content: str
    ) -> None:
        """
        Add a message to the conversation history.

        Args:
            session_id: The unique identifier for the conversation session
            role: The role of the message sender ('user' or 'assistant')
            content: The content of the message
        """
        try:
            # Ensure the session exists
            if session_id not in self.conversations:
                logger.debug(f"Creating new conversation history for session {session_id}")
                self.conversations[session_id] = []

            # Add the message
            self.conversations[session_id].append({
                "role": role,
                "content": content
            })

            # Truncate history if needed (keep last 20 messages)
            if len(self.conversations[session_id]) > 20:
                self.conversations[session_id] = self.conversations[session_id][-20:]
                logger.debug(f"Truncated conversation history for session {session_id}")

            logger.debug(f"Added {role} message to session {session_id}")

        except Exception as e:
            logger.error(f"Error adding message to conversation: {str(e)}")

    def get_conversation_history(
            self,
            session_id: str,
            max_messages: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Get the conversation history for a session.

        Args:
            session_id: The unique identifier for the conversation session
            max_messages: The maximum number of messages to return (most recent)

        Returns:
            A list of message dictionaries with 'role' and 'content' keys
        """
        try:
            # Return empty list if session doesn't exist
            if session_id not in self.conversations:
                logger.debug(f"No conversation history found for session {session_id}")
                return []

            history = self.conversations[session_id]

            # Limit to max_messages if specified
            if max_messages is not None and max_messages > 0:
                history = history[-max_messages:]

            logger.debug(f"Retrieved {len(history)} messages for session {session_id}")
            return history

        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
            return []

    def update_context(
            self,
            session_id: str,
            context_updates: Dict[str, Any]
    ) -> None:
        """
        Update the context for a session.

        Args:
            session_id: The unique identifier for the conversation session
            context_updates: Dictionary of context updates to apply
        """
        try:
            # Ensure the session exists
            if session_id not in self.contexts:
                logger.debug(f"Creating new context for session {session_id}")
                self.contexts[session_id] = {}

            # Update the context
            self.contexts[session_id].update(context_updates)
            logger.debug(f"Updated context for session {session_id}")

        except Exception as e:
            logger.error(f"Error updating context: {str(e)}")

    def get_context(self, session_id: str) -> Dict[str, Any]:
        """
        Get the context for a session.

        Args:
            session_id: The unique identifier for the conversation session

        Returns:
            A dictionary of context information
        """
        try:
            # Return empty dict if session doesn't exist
            if session_id not in self.contexts:
                logger.debug(f"No context found for session {session_id}")
                return {}

            logger.debug(f"Retrieved context for session {session_id}")
            return self.contexts[session_id]

        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return {}

    def reset_session(self, session_id: str) -> None:
        """
        Reset the conversation history and context for a session.

        Args:
            session_id: The unique identifier for the conversation session
        """
        try:
            # Clear conversation history
            if session_id in self.conversations:
                self.conversations[session_id] = []

            # Clear context
            if session_id in self.contexts:
                self.contexts[session_id] = {}

            logger.debug(f"Reset conversation and context for session {session_id}")

        except Exception as e:
            logger.error(f"Error resetting session: {str(e)}")