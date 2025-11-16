# src/database/models.py
"""Database models for conversation storage."""

from sqlalchemy import Column, String, Text, DateTime, Integer, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import json

Base = declarative_base()


class Conversation(Base):
    """Conversation model."""
    
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    messages = Column(Text)  # Store as JSON string
    meta_data = Column(Text)  # Changed from 'metadata' to 'meta_data' - FIXED!
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "conversation_id": self.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": json.loads(self.messages) if self.messages else [],
            "metadata": json.loads(self.meta_data) if self.meta_data else {}
        }


class Message(Base):
    """Individual message model."""
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String, index=True)
    role = Column(String)  # 'user' or 'assistant'
    content = Column(Text)
    intent = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    meta_data = Column(Text)  # Changed from 'metadata' to 'meta_data' - FIXED!
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "intent": self.intent,
            "timestamp": self.timestamp.isoformat(),
            "metadata": json.loads(self.meta_data) if self.meta_data else {}
        }