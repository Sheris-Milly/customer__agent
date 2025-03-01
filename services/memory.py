# services/memory.py
from langchain.memory import ConversationBufferMemory
import logging

logger = logging.getLogger(__name__)

# Create a conversation memory that works with the agent
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

logger.info("Conversation memory initialized")