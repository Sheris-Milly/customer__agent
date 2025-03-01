# chatbot_agents/chatbot_agent.py
from langchain.agents import create_react_agent, AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import StructuredTool
import logging
from models.deepseek_model import llm
from services.memory import memory
from services.faq_retrieval import get_faq_answer
from services.order_tracking import track_order

logger = logging.getLogger(__name__)

# Define the tools using the updated StructuredTool format
faq_tool = StructuredTool.from_function(
    func=get_faq_answer,
    name="FAQ_Retriever",
    description="Provides answers to common questions from our FAQ database. Use this for general product questions."
)

track_order_tool = StructuredTool.from_function(
    func=track_order,
    name="Order_Tracker",
    description="Check the status of an order by providing an order ID (e.g., ABC123)."
)

# Define the list of tools for the agent
tools = [track_order_tool, faq_tool]

# Create a prompt for the agent with updated format
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful customer service AI assistant.
You have access to the following tools:
{tools}

Always use these tools when appropriate to provide accurate information to customers.
If you don't know the answer, just say you don't know."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Initialize the chatbot agent with tools, LLM, and conversation memory
try:
    # Create the agent using create_react_agent
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    # Create an agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True
    )


    # Define a simple run method to maintain backward compatibility
    def run(input_text):
        try:
            return agent_executor.invoke({"input": input_text})["output"]
        except Exception as e:
            logger.error(f"Error in agent execution: {str(e)}")
            return "I'm having trouble processing your request. Please try again or ask a different question."


    # Add the run method to the agent_executor for backward compatibility
    agent_executor.run = run

    logger.info("Chatbot agent initialized successfully with updated LangChain format")

except Exception as e:
    logger.error(f"Failed to initialize agent: {str(e)}")


    # Create a simple function to use as fallback
    def simple_response(query: str) -> str:
        return "I'm sorry, but I'm currently experiencing technical difficulties. Please try again later."


    # Create a minimal agent interface for graceful failure
    class FallbackAgent:
        def run(self, query: str) -> str:
            logger.warning(f"Using fallback agent for query: {query}")
            return simple_response(query)

        def invoke(self, inputs: dict) -> dict:
            logger.warning(f"Using fallback agent invoke for query: {inputs.get('input', '')}")
            return {"output": simple_response(inputs.get("input", ""))}


    agent_executor = FallbackAgent()
    logger.warning("Using fallback agent due to initialization failure")