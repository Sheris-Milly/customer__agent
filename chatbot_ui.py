import streamlit as st
from chatbot_agents.chatbot_agent import agent  # Import the chatbot agent
import logging
logging.basicConfig(level=logging.ERROR)
st.title("Customer Service Chatbot - DeepSeek R1")

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Ask me anything:", key="user_input")

if st.button("Send"):
    if user_input:
        response = agent.run(user_input)
        st.session_state.chat_history.append({"user": user_input, "bot": response})
        st.session_state.user_input = ""  # Clear input

# Display conversation history
for chat in st.session_state.chat_history:
    st.markdown(f"**User:** {chat['user']}")
    st.markdown(f"**Bot:** {chat['bot']}")

