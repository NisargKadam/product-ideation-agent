# src/agents/graph.py
"""LangGraph workflow definition."""

from langgraph.graph import StateGraph, END
from src.models.state import AgentState
from src.agents.nodes import AgentNodes
import structlog

logger = structlog.get_logger()


def create_agent_graph():
    """Create and compile the agent graph."""
    
    # Initialize nodes
    nodes = AgentNodes()
    
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("classify_intent", nodes.classify_intent)
    workflow.add_node("trend_research", nodes.trend_research)
    workflow.add_node("concept_generation", nodes.concept_generation)
    workflow.add_node("general_response", nodes.general_response)
    workflow.add_node("synthesize", nodes.synthesize_response)
    
    # Set entry point
    workflow.set_entry_point("classify_intent")
    
    # Add conditional routing based on intent
    def route_by_intent(state: AgentState) -> str:
        """Route to appropriate node based on classified intent."""
        intent = state.get("user_intent", "general_chat")
        
        logger.info("Routing decision", intent=intent)
        
        if intent == "trend_research":
            return "trend_research"
        elif intent == "concept_generation":
            return "concept_generation"
        else:
            # Handle competitive_analysis, validation, general_chat
            return "general_response"
    
    workflow.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "trend_research": "trend_research",
            "concept_generation": "concept_generation",
            "general_response": "general_response"
        }
    )
    
    # All paths lead to synthesize
    workflow.add_edge("trend_research", "synthesize")
    workflow.add_edge("concept_generation", "synthesize")
    workflow.add_edge("general_response", "synthesize")
    
    # End after synthesis
    workflow.add_edge("synthesize", END)
    
    # Compile the graph
    app = workflow.compile()
    
    logger.info("Agent graph compiled successfully")
    
    return app