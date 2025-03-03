import logging
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional

from config import API_HOST, API_PORT
from chatbot_agents.chatbot_agent import ChatbotAgent

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("chatbot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Customer Service Chatbot API")

# Initialize the chatbot agent
chatbot_agent = ChatbotAgent()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str
    context: Optional[Dict] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    context: Optional[Dict] = None


@app.get("/")
async def root():
    return {"message": "Customer Service Chatbot API is running"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        logger.debug(f"Received chat request: {request.message} (Session ID: {request.session_id})")

        # Process the chat request using the chatbot agent
        response, context = chatbot_agent.process_message(
            request.message,
            request.session_id,
            request.context
        )

        logger.debug(f"Generated response: {response} (Session ID: {request.session_id})")

        return ChatResponse(
            response=response,
            session_id=request.session_id,
            context=context
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/faq", response_model=List[Dict])
async def get_faqs():
    try:
        faqs = chatbot_agent.get_faqs()
        return faqs
    except Exception as e:
        logger.error(f"Error retrieving FAQs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/track_order/{order_id}")
async def track_order(order_id: str):
    try:
        logger.debug(f"Tracking order: {order_id}")
        order_info = chatbot_agent.track_order(order_id)
        return order_info
    except Exception as e:
        logger.error(f"Error tracking order {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset_chat")
async def reset_chat(request: Request):
    data = await request.json()
    session_id = data.get("session_id")

    try:
        logger.debug(f"Resetting chat for session: {session_id}")
        chatbot_agent.reset_conversation(session_id)
        return {"message": f"Chat session {session_id} has been reset"}
    except Exception as e:
        logger.error(f"Error resetting chat session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    logger.info(f"Starting Customer Service Chatbot API on {API_HOST}:{API_PORT}")
    uvicorn.run(app, host=API_HOST, port=API_PORT)