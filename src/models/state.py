# src/models/state.py
"""State definitions for LangGraph agent."""

from typing import TypedDict, List, Dict, Optional, Annotated
from datetime import datetime
import operator


class AgentState(TypedDict):
    """State that the agent maintains throughout conversation."""
    
    # Conversation
    messages: Annotated[List[Dict], operator.add]  # Chat history
    conversation_id: str  # Unique conversation ID
    
    # User Context
    user_intent: Optional[str]  # classified intent: trend_research, concept_generation, etc.
    user_query: str  # Current user query
    
    # Research & Analysis
    search_results: Optional[Dict]  # Results from trend research
    analysis: Optional[Dict]  # Analysis of data
    recommendations: Optional[List[Dict]]  # Generated recommendations
    
    # Metadata
    timestamp: str  # Current timestamp
    iteration: int  # Number of processing iterations