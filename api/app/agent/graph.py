"""
LangGraph agent for skincare consultation.
Implements a stateful conversation graph with tool usage.
"""
from typing import TypedDict, Annotated, Sequence, Optional, Dict, Any, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
import os
import logging

from .tools import AGENT_TOOLS

logger = logging.getLogger(__name__)

# Define the state
class AgentState(TypedDict):
    """State for the skincare agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    skin_analysis: Optional[Dict[str, Any]]
    user_location: Optional[Dict[str, str]]
    next_action: Optional[str]

# Initialize LLM
def create_llm():
    """Create the LLM with tool binding."""
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        logger.warning("GROQ_API_KEY not set, agent will not function properly")
        return None
    
    llm = ChatGroq(
        model="mixtral-8x7b-32768",
        temperature=0.7,
        groq_api_key=api_key
    )
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(AGENT_TOOLS)
    return llm_with_tools

# Define the system prompt
SYSTEM_PROMPT = """You are Hasna, a friendly skincare expert assistant. You help users understand their skin and find the right products.

CONVERSATION STYLE:
- Keep responses SHORT and conversational (2-4 sentences for simple questions)
- Ask follow-up questions to keep the conversation flowing
- Be warm and natural, like texting a friend
- NEVER use tables or bullet points - write in flowing paragraphs

AVAILABLE TOOLS:
- analyze_skin_image: Analyze a user's skin from an image
- get_product_recommendations: Get personalized product recommendations
- find_nearby_stores: Find stores near the user

WHEN TO USE TOOLS:
- If the user uploads an image, use analyze_skin_image
- If they ask for product recommendations and you have their skin profile, use get_product_recommendations
- If they ask about nearby stores and you have their location, use find_nearby_stores

IMPORTANT:
- Always be helpful and supportive
- Recommend seeing a dermatologist for serious concerns
- Keep the conversation natural and engaging
"""

def should_continue(state: AgentState) -> str:
    """Determine if we should continue or end."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # If the LLM makes a tool call, route to tools
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    # Otherwise, end
    return END

def call_model(state: AgentState) -> Dict[str, Any]:
    """Call the LLM with the current state."""
    messages = state["messages"]
    
    # Add system message if not present
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
    
    # Add skin analysis context if available
    if state.get("skin_analysis"):
        context_msg = f"\n\nUSER'S SKIN PROFILE:\n"
        skin_data = state["skin_analysis"]
        if skin_data.get("skinType"):
            context_msg += f"Skin Type: {skin_data['skinType'].get('type')}\n"
        if skin_data.get("skinIssues"):
            issues = [issue.get('name') for issue in skin_data['skinIssues']]
            context_msg += f"Issues: {', '.join(issues)}\n"
        
        # Update system message
        messages[0] = SystemMessage(content=SYSTEM_PROMPT + context_msg)
    
    llm = create_llm()
    if not llm:
        return {
            "messages": [AIMessage(content="I'm currently unavailable. Please try again later.")]
        }
    
    response = llm.invoke(messages)
    return {"messages": [response]}

def create_agent_graph():
    """Create and compile the agent graph."""
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(AGENT_TOOLS))
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    
    # Add edge from tools back to agent
    workflow.add_edge("tools", "agent")
    
    # Compile
    app = workflow.compile()
    return app

# Create the compiled graph (singleton)
_compiled_graph = None

def get_agent_graph():
    """Get or create the compiled agent graph."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = create_agent_graph()
    return _compiled_graph
