# src/database/manager.py
"""Database manager for handling database operations."""

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session
from src.database.models import Base, Conversation, Message
from typing import List, Optional, Dict
import json
from datetime import datetime
import structlog

logger = structlog.get_logger()


class DatabaseManager:
    """Manager for database operations."""
    
    def __init__(self, database_url: str):
        """Initialize database manager."""
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        logger.info("Database initialized", database_url=database_url)
    
    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()
    
    # Conversation Operations
    
    def create_conversation(self, conversation_id: str, metadata: Dict = None) -> Conversation:
        """Create a new conversation."""
        session = self.get_session()
        try:
            conversation = Conversation(
                id=conversation_id,
                messages=json.dumps([]),
                meta_data=json.dumps(metadata or {})  # FIXED: metadata → meta_data
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            logger.info("Conversation created", conversation_id=conversation_id)
            return conversation
        finally:
            session.close()
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        session = self.get_session()
        try:
            conversation = session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            return conversation
        finally:
            session.close()
    
    def update_conversation_messages(self, conversation_id: str, messages: List[Dict]):
        """Update conversation messages."""
        session = self.get_session()
        try:
            conversation = session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if conversation:
                conversation.messages = json.dumps(messages)
                conversation.updated_at = datetime.utcnow()
                session.commit()
                logger.info("Conversation updated", conversation_id=conversation_id)
            else:
                logger.warning("Conversation not found", conversation_id=conversation_id)
        finally:
            session.close()
    
    def list_conversations(self, limit: int = 50, offset: int = 0) -> List[Conversation]:
        """List all conversations."""
        session = self.get_session()
        try:
            conversations = session.query(Conversation).order_by(
                desc(Conversation.updated_at)
            ).limit(limit).offset(offset).all()
            return conversations
        finally:
            session.close()
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        session = self.get_session()
        try:
            conversation = session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if conversation:
                # Delete associated messages
                session.query(Message).filter(
                    Message.conversation_id == conversation_id
                ).delete()
                
                # Delete conversation
                session.delete(conversation)
                session.commit()
                logger.info("Conversation deleted", conversation_id=conversation_id)
                return True
            return False
        finally:
            session.close()
    
    # Message Operations
    
    def add_message(
        self, 
        conversation_id: str, 
        role: str, 
        content: str, 
        intent: Optional[str] = None,
        metadata: Dict = None
    ) -> Message:
        """Add a message to the database."""
        session = self.get_session()
        try:
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                intent=intent,
                meta_data=json.dumps(metadata or {})  # FIXED: metadata → meta_data
            )
            session.add(message)
            session.commit()
            session.refresh(message)
            logger.info("Message added", conversation_id=conversation_id, role=role)
            return message
        finally:
            session.close()
    
    def get_messages(self, conversation_id: str) -> List[Message]:
        """Get all messages for a conversation."""
        session = self.get_session()
        try:
            messages = session.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.timestamp).all()
            return messages
        finally:
            session.close()
    
    def get_conversation_with_messages(self, conversation_id: str) -> Optional[Dict]:
        """Get conversation with all messages."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        messages = self.get_messages(conversation_id)
        
        return {
            "conversation_id": conversation.id,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "messages": [msg.to_dict() for msg in messages],
            "metadata": json.loads(conversation.meta_data) if conversation.meta_data else {}  # FIXED
        }