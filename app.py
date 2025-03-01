# app.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import time
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define API settings
API_HOST = os.environ.get("API_HOST", "0.0.0.0")
API_PORT = int(os.environ.get("API_PORT", "8000"))

app = FastAPI(title="DeepSeek R1 Customer Service API")

# Add CORS middleware to allow Streamlit to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatInput(BaseModel):
    message: str
    session_id: str = "default"  # Allow tracking different conversations


# Import the agent only after defining the app
# This prevents circular imports and gives time for logging to initialize
try:
    # Import agent_executor instead of agent
    from chatbot_agents.chatbot_agent import agent_executor as agent

    logger.info("Agent imported successfully")
except Exception as e:
    logger.error(f"Error importing agent: {str(e)}")


    # Define a fallback agent
    class FallbackAgent:
        def run(self, input_text):
            return "I'm sorry, but the service is currently unavailable. Please try again later."


    agent = FallbackAgent()
    logger.warning("Using fallback agent due to import failure")


@app.post("/chat")
async def chat(input_data: ChatInput):
    try:
        start_time = time.time()
        logger.info(f"Received message from session {input_data.session_id}: {input_data.message}")

        # Process the message with the agent using invoke instead of run
        try:
            # Try the new invoke method first
            response = agent.invoke({"input": input_data.message})
            if isinstance(response, dict) and "output" in response:
                result = response["output"]
            else:
                result = str(response)
        except AttributeError:
            # Fall back to run method if invoke isn't available
            logger.info("Falling back to agent.run method")
            result = agent.run(input_data.message)

        # Log timing information
        processing_time = time.time() - start_time
        logger.info(f"Processed message in {processing_time:.2f} seconds")

        return {"response": result, "session_id": input_data.session_id}

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please try again later."}
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "DeepSeek R1 Customer Service API is running. Use /chat endpoint to interact."}


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting API server on {API_HOST}:{API_PORT}")
    uvicorn.run(app, host=API_HOST, port=API_PORT)