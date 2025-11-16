# test_db.py
"""Test database directly."""

from src.database import DatabaseManager
from src.config import settings

# Initialize database
db = DatabaseManager(settings.database_url)

# List all conversations
conversations = db.list_conversations()

print(f"\n{'='*50}")
print(f"Total Conversations: {len(conversations)}")
print(f"{'='*50}\n")

for conv in conversations:
    print(f"Conversation ID: {conv.id}")
    print(f"Created: {conv.created_at}")
    print(f"Updated: {conv.updated_at}")
    
    # Get messages
    messages = db.get_messages(conv.id)
    print(f"Messages: {len(messages)}")
    
    for msg in messages:
        print(f"  [{msg.role}]: {msg.content[:50]}...")
    
    print(f"{'-'*50}\n")