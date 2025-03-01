# chatbot_ui.py
import streamlit as st
import requests
import json
import logging
import uuid
import time
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set up API endpoint
API_URL = os.environ.get("API_URL", "http://localhost:8000/chat")

# Set page title and configure layout
st.set_page_config(
    page_title="Customer Service Chatbot - DeepSeek R1",
    page_icon="💬",
    layout="centered"
)

# Custom CSS to improve the appearance
st.markdown("""
<style>
.chat-message {
    padding: 1.5rem; 
    border-radius: 0.5rem; 
    margin-bottom: 1rem; 
    display: flex;
    flex-direction: column;
}
.chat-message.user {
    background-color: #f0f2f6;
}
.chat-message.bot {
    background-color: #e6f7ff;
}
.chat-header {
    color: #0066cc;
    margin-bottom: 0.5rem;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("Customer Service Chatbot 💬")
st.markdown("Ask questions about orders, products, or services!")

# Initialize session state for chat history and session ID
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    logger.info(f"New session started: {st.session_state.session_id}")

# User input area
with st.form(key="message_form", clear_on_submit=True):
    user_input = st.text_area("Type your message:", key="user_input", height=100)
    col1, col2 = st.columns([1, 5])
    with col1:
        submit_button = st.form_submit_button("Send")

# Process user input when submitted
if submit_button and user_input:
    # Display user message
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    try:
        # Show a spinner while waiting for response
        with st.spinner("Thinking..."):
            start_time = time.time()

            # Make API request to the backend
            response = requests.post(
                API_URL,
                json={"message": user_input, "session_id": st.session_state.session_id},
                timeout=120  # Longer timeout for LLM processing
            )

            # Check if request was successful
            if response.status_code == 200:
                bot_response = response.json().get("response", "Sorry, I couldn't process your request.")
                st.session_state.chat_history.append({"role": "bot", "content": bot_response})

                # Log processing time
                processing_time = time.time() - start_time
                logger.info(f"Response received in {processing_time:.2f} seconds")
            else:
                error_msg = f"Error: {response.status_code} - {response.text}"
                st.session_state.chat_history.append({"role": "bot",
                                                      "content": "I'm having trouble connecting to my brain right now. Please try again later."})
                logger.error(error_msg)

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        st.session_state.chat_history.append({"role": "bot",
                                              "content": "I'm having trouble connecting to the server. Please check your connection and try again."})

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        st.session_state.chat_history.append(
            {"role": "bot", "content": "An unexpected error occurred. Please try again."})

# Display chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f'<div class="chat-message user"><div class="chat-header">You</div>{message["content"]}</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message bot"><div class="chat-header">Bot</div>{message["content"]}</div>',
                    unsafe_allow_html=True)

# Add a clear button to reset the conversation
if st.button("Clear Conversation"):
    st.session_state.chat_history = []
    st.session_state.session_id = str(uuid.uuid4())
    logger.info(f"Conversation cleared, new session: {st.session_state.session_id}")
    st.experimental_rerun()

# Add information footer
st.markdown("---")
st.markdown("Built with DeepSeek R1 - Powered by Open-Source LLMs")