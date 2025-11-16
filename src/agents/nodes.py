# src/agents/nodes.py
"""Agent nodes - individual processing units in the graph."""

from src.models.state import AgentState
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.config import settings
from src.tools import web_search_tool  # ADD THIS IMPORT
import structlog
from datetime import datetime

logger = structlog.get_logger()


class AgentNodes:
    """Collection of agent processing nodes."""
    
    def __init__(self):
        """Initialize with LLM."""
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.7,
            api_key=settings.openai_api_key
        )
    
    def classify_intent(self, state: AgentState) -> AgentState:
        """Classify user intent from their message."""
        logger.info("Node: classify_intent", query=state["user_query"])
        
        system_prompt = """You are an intent classifier for a Product Ideation Agent in the F&B industry.

Classify the user's intent into ONE of these categories:
1. trend_research - User wants to know about trends, what's popular, market insights
2. concept_generation - User wants new product ideas or concepts
3. competitive_analysis - User wants to know about competitors
4. validation - User wants to validate an existing idea
5. general_chat - General conversation, greetings, unclear intent

Respond with ONLY the category name, nothing else."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=state["user_query"])
        ]
        
        response = self.llm.invoke(messages)
        intent = response.content.strip().lower()
        
        logger.info("Intent classified", intent=intent)
        
        state["user_intent"] = intent
        state["iteration"] += 1
        
        return state
    
    def trend_research(self, state: AgentState) -> AgentState:
        """Research trends based on user query - NOW WITH WEB SEARCH!"""
        logger.info("Node: trend_research", query=state["user_query"])
        
        # Step 1: Search the web for current trends
        search_query = f"food beverage trends 2025 {state['user_query']}"
        search_results = web_search_tool.search(search_query, max_results=5)
        
        # Step 2: Search for recent news
        news_results = web_search_tool.search_news(
            f"{state['user_query']} food trends", 
            max_results=3
        )
        
        # Step 3: Format search results for LLM
        search_context = "### Web Search Results:\n"
        for i, result in enumerate(search_results, 1):
            search_context += f"\n{i}. **{result['title']}**\n"
            search_context += f"   {result['snippet']}\n"
            search_context += f"   URL: {result['url']}\n"
        
        search_context += "\n### Recent News:\n"
        for i, result in enumerate(news_results, 1):
            search_context += f"\n{i}. **{result['title']}** ({result.get('source', 'N/A')})\n"
            search_context += f"   {result['snippet']}\n"
        
        # Step 4: Analyze with LLM
        system_prompt = """You are a food & beverage trend researcher with access to current market data.

Analyze the search results provided and create a comprehensive trend report with:
1. **Top 3-5 Trends**: What's currently popular and emerging
2. **Data & Statistics**: Growth indicators, market size, consumer adoption
3. **Target Demographics**: Who's driving these trends
4. **Market Examples**: Real products/brands mentioned in the results
5. **Actionable Insights**: How F&B companies can capitalize

Be specific, cite the sources when possible, and focus on actionable intelligence."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User Query: {state['user_query']}\n\n{search_context}")
        ]
        
        response = self.llm.invoke(messages)
        
        state["search_results"] = {
            "type": "trend_research",
            "content": response.content,
            "raw_search_results": search_results,
            "raw_news_results": news_results,
            "timestamp": datetime.now().isoformat()
        }
        
        state["iteration"] += 1
        
        return state
    
    def concept_generation(self, state: AgentState) -> AgentState:
        """Generate product concepts."""
        logger.info("Node: concept_generation", query=state["user_query"])
        
        system_prompt = """You are a creative product developer for F&B brands.

Generate 3 innovative product concepts based on the user's request.

For each concept provide:
1. Product Name
2. Description (2-3 sentences)
3. Target Audience
4. Key Differentiator
5. Suggested Price Tier (Budget/Mid/Premium)

Be creative but realistic and market-viable."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Generate product concepts for: {state['user_query']}")
        ]
        
        response = self.llm.invoke(messages)
        
        state["analysis"] = {
            "type": "concept_generation",
            "content": response.content,
            "timestamp": datetime.now().isoformat()
        }
        
        state["iteration"] += 1
        
        return state
    
    def general_response(self, state: AgentState) -> AgentState:
        """Handle general conversation."""
        logger.info("Node: general_response", query=state["user_query"])
        
        system_prompt = """You are a friendly Product Ideation Assistant for the F&B industry.

Respond naturally to the user. If they're greeting you or making small talk, be warm and helpful.
If their request is unclear, ask clarifying questions to understand what they need help with.

You can help with:
- Researching food & beverage trends (with real-time web search)
- Generating new product concepts
- Analyzing competitors
- Validating product ideas"""

        # Include recent conversation history
        messages = [SystemMessage(content=system_prompt)]
        
        # Add last 5 messages for context
        recent_messages = state["messages"][-5:] if len(state["messages"]) > 0 else []
        for msg in recent_messages:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
        
        # Add current query
        messages.append(HumanMessage(content=state["user_query"]))
        
        response = self.llm.invoke(messages)
        
        state["analysis"] = {
            "type": "general_chat",
            "content": response.content,
            "timestamp": datetime.now().isoformat()
        }
        
        state["iteration"] += 1
        
        return state
    
    def synthesize_response(self, state: AgentState) -> AgentState:
        """Synthesize final response to user."""
        logger.info("Node: synthesize_response")
        
        # Determine what content to return based on what was generated
        if state.get("analysis"):
            response_content = state["analysis"]["content"]
        elif state.get("search_results"):
            response_content = state["search_results"]["content"]
        else:
            response_content = "I'm ready to help you with product ideation. What would you like to explore?"
        
        # Add to messages
        state["messages"].append({
            "role": "assistant",
            "content": response_content,
            "timestamp": datetime.now().isoformat()
        })
        
        state["iteration"] += 1
        
        logger.info("Response synthesized", iteration=state["iteration"])
        
        return state