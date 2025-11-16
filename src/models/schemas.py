# src/models/schemas.py
"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class ChatMessage(BaseModel):
    """Single chat message."""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Request to chat with the agent."""
    message: str = Field(..., description="User message", min_length=1)
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    user_context: Optional[Dict] = Field(default_factory=dict, description="Additional user context")


class ChatResponse(BaseModel):
    """Response from the agent."""
    message: str = Field(..., description="Agent response")
    conversation_id: str = Field(..., description="Conversation ID")
    intent: Optional[str] = Field(None, description="Detected user intent")
    recommendations: Optional[List[Dict]] = Field(None, description="Product recommendations if any")
    metadata: Optional[Dict] = Field(default_factory=dict, description="Additional metadata")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    app_name: str
    version: str
    timestamp: datetime