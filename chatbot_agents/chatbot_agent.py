from langchain.agents import initialize_agent, AgentType, Tool
from models.deepseek_model import llm
from services.memory import memory
from services.faq_retrieval import get_faq_answer
from services.order_tracking import track_order_tool

# Create a FAQ retrieval tool
faq_tool = Tool(
    name="FAQ Retriever",
    func=get_faq_answer,
    description="Provides answers to common questions from our FAQ database."
)

# Define the list of tools for the agent
tools = [track_order_tool, faq_tool]

# Initialize the chatbot agent with tools, LLM, and conversation memory
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    memory=memory,
    verbose=True
)
