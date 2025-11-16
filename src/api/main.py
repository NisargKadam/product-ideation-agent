# src/api/main.py
"""FastAPI application for the Product Ideation Agent."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.models.schemas import ChatRequest, ChatResponse, HealthResponse
from src.agents.graph import create_agent_graph
from src.config import settings
from src import __version__
from src.database import DatabaseManager
import structlog
from datetime import datetime
import uuid
import os

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description="AI-powered product ideation assistant for F&B industry"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Initialize database
db_manager = DatabaseManager(settings.database_url)

# Initialize agent graph
agent_graph = create_agent_graph()


@app.get("/ui")
async def serve_ui():
    """Serve the chat UI."""
    frontend_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(frontend_file):
        return FileResponse(frontend_file)
    else:
        raise HTTPException(status_code=404, detail="Frontend not found")


@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=__version__,
        timestamp=datetime.now()
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the Product Ideation Agent."""
    
    try:
        # Generate or use existing conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Get or create conversation from database
        conversation = db_manager.get_conversation(conversation_id)
        
        if not conversation:
            # Create new conversation
            conversation = db_manager.create_conversation(
                conversation_id=conversation_id,
                metadata=request.user_context
            )
            messages = []
        else:
            # Get existing messages
            conv_data = db_manager.get_conversation_with_messages(conversation_id)
            messages = conv_data["messages"] if conv_data else []
        
        logger.info(
            "Chat request received",
            conversation_id=conversation_id,
            message=request.message
        )
        
        # Prepare initial state
        initial_state = {
            "messages": [{"role": m["role"], "content": m["content"], "timestamp": m["timestamp"]} for m in messages],
            "conversation_id": conversation_id,
            "user_intent": None,
            "user_query": request.message,
            "search_results": None,
            "analysis": None,
            "recommendations": None,
            "timestamp": datetime.now().isoformat(),
            "iteration": 0
        }
        
        # Add user message
        initial_state["messages"].append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Save user message to database
        db_manager.add_message(
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )
        
        # Run the agent
        final_state = agent_graph.invoke(initial_state)
        
        # Extract assistant's response
        assistant_message = final_state["messages"][-1]["content"]
        intent = final_state.get("user_intent")
        
        # Save assistant message to database
        db_manager.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_message,
            intent=intent,
            metadata={
                "iterations": final_state["iteration"],
                "timestamp": final_state["timestamp"]
            }
        )
        
        logger.info(
            "Chat response generated",
            conversation_id=conversation_id,
            intent=intent
        )
        
        return ChatResponse(
            message=assistant_message,
            conversation_id=conversation_id,
            intent=intent,
            recommendations=final_state.get("recommendations"),
            metadata={
                "iterations": final_state["iteration"],
                "timestamp": final_state["timestamp"]
            }
        )
    
    except Exception as e:
        logger.error("Error processing chat request", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/conversations")
async def list_conversations(limit: int = 50, offset: int = 0):
    """List all conversations."""
    conversations = db_manager.list_conversations(limit=limit, offset=offset)
    return {
        "conversations": [conv.to_dict() for conv in conversations],
        "total": len(conversations)
    }


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history with messages."""
    conversation = db_manager.get_conversation_with_messages(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    success = db_manager.delete_conversation(conversation_id)
    
    if success:
        return {"message": "Conversation deleted", "conversation_id": conversation_id}
    
    raise HTTPException(status_code=404, detail="Conversation not found")