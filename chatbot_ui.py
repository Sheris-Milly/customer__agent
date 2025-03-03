import streamlit as st
import requests
import json
import logging
import uuid
import time
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("chatbot_ui.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# API Configuration
API_URL = "http://localhost:8000"



def filter_response(response: str) -> str:
    # Split the response using the marker </think>
    parts = response.split("</think>")
    # Return the part after the marker if it exists; otherwise, return the full response.
    return parts[-1].strip() if len(parts) > 1 else response


def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        logger.debug(f"Generated new session ID: {st.session_state.session_id}")

    if "messages" not in st.session_state:
        st.session_state.messages = []
        logger.debug("Initialized empty messages list")

    if "context" not in st.session_state:
        st.session_state.context = {}
        logger.debug("Initialized empty context dictionary")


def reset_conversation():
    """Reset the conversation state."""
    try:
        response = requests.post(
            f"{API_URL}/reset_chat",
            json={"session_id": st.session_state.session_id}
        )

        if response.status_code == 200:
            st.session_state.messages = []
            st.session_state.context = {}
            logger.debug(f"Successfully reset conversation for session {st.session_state.session_id}")
            st.success("Conversation has been reset!")
        else:
            logger.error(f"Failed to reset conversation: {response.text}")
            st.error(f"Failed to reset conversation: {response.text}")
    except Exception as e:
        logger.error(f"Error resetting conversation: {str(e)}")
        st.error(f"Error resetting conversation: {str(e)}")


def send_message(message: str):
    """Send a message to the chatbot API and display the response."""
    if message:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": message})

        with st.spinner("Thinking..."):
            try:
                logger.debug(f"Sending message to API: {message}")
                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "message": message,
                        "session_id": st.session_state.session_id,
                        "context": st.session_state.context
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    bot_response = data.get("response", "I couldn't process your request.")
                    st.session_state.context = data.get("context", {})
                    logger.debug(f"Received response: {bot_response}")

                    # Add bot response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                else:
                    error_msg = f"Error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": f"Sorry, I encountered an error: {error_msg}"})
            except Exception as e:
                error_msg = f"Failed to communicate with the chatbot service: {str(e)}"
                logger.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": f"Sorry, I encountered an error: {error_msg}"})

def send_message(message: str):
    if message:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": message})

        with st.spinner("Thinking..."):
            try:
                logger.debug(f"Sending message to API: {message}")
                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "message": message,
                        "session_id": st.session_state.session_id,
                        "context": st.session_state.context
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    bot_response = data.get("response", "I couldn't process your request.")

                    # Filter out any chain-of-thought
                    bot_response = filter_response(bot_response)

                    st.session_state.context = data.get("context", {})
                    logger.debug(f"Received response: {bot_response}")

                    # Add filtered bot response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                else:
                    error_msg = f"Error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": f"Sorry, I encountered an error: {error_msg}"}
                    )
            except Exception as e:
                error_msg = f"Failed to communicate with the chatbot service: {str(e)}"
                logger.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": f"Sorry, I encountered an error: {error_msg}"}
                )




def track_order(order_id: str):
    """Track an order using the chatbot API."""
    try:
        logger.debug(f"Tracking order: {order_id}")
        response = requests.get(f"{API_URL}/track_order/{order_id}")

        if response.status_code == 200:
            order_info = response.json()
            logger.debug(f"Order info received: {order_info}")
            return order_info
        else:
            logger.error(f"Error tracking order: {response.status_code} - {response.text}")
            return {"error": f"Failed to track order: {response.text}"}
    except Exception as e:
        logger.error(f"Exception tracking order: {str(e)}")
        return {"error": f"Failed to track order: {str(e)}"}


def get_faqs():
    """Get the list of FAQs from the chatbot API."""
    try:
        logger.debug("Retrieving FAQs")
        response = requests.get(f"{API_URL}/faq")

        if response.status_code == 200:
            faqs = response.json()
            logger.debug(f"Retrieved {len(faqs)} FAQs")
            return faqs
        else:
            logger.error(f"Error retrieving FAQs: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        logger.error(f"Exception retrieving FAQs: {str(e)}")
        return []


def main():
    st.set_page_config(
        page_title="Customer Service Agent ",
        page_icon="💬",
        layout="wide"
    )

    # Initialize session state
    initialize_session_state()

    # Sidebar with tools
    with st.sidebar:
        st.title("Customer Service Tools")

        # Order tracking
        st.subheader("Track Your Order")
        order_id = st.text_input("Enter Order ID")
        track_button = st.button("Track Order")

        if track_button and order_id:
            order_info = track_order(order_id)
            if "error" in order_info:
                st.error(order_info["error"])
            else:
                st.success(f"Order #{order_id} Status: {order_info.get('status', 'Unknown')}")
                st.json(order_info)

        # FAQ section
        st.subheader("Frequently Asked Questions")
        faqs = get_faqs()
        if faqs:
            for i, faq in enumerate(faqs):
                with st.expander(faq["question"]):
                    st.write(faq["answer"])
        else:
            st.info("No FAQs available")

        # Reset conversation button
        st.subheader("Chat Controls")
        if st.button("Reset Conversation"):
            reset_conversation()

    # Main chat interface
    st.title("Customer Service Agent based on DeepSeek R1")
    st.caption("How can I help you today?")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    user_input = st.chat_input("Type your message here...")
    if user_input:
        send_message(user_input)
        # This forces a rerun to display the new messages
        st.rerun()


if __name__ == "__main__":
    main()