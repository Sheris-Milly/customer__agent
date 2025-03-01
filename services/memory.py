from langchain.memory import ConversationBufferMemory

# Define conversation memory with a specific memory key
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
