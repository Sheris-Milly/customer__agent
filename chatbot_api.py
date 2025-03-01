from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.chatbot_agent import agent  # Import the chatbot agent



app = FastAPI()

class ChatInput(BaseModel):
    message: str

@app.post("/chat")
async def chat(input_data: ChatInput):
    try:
        # Depending on your agent implementation, you might consider using an async method (e.g. await agent.arun(...))
        response = agent.run(input_data.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
