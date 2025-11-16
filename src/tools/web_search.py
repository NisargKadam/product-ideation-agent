# src/tools/web_search.py
"""Web search tools for the agent."""

from typing import List, Dict, Optional
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
import structlog
import requests
from bs4 import BeautifulSoup

logger = structlog.get_logger()


class WebSearchTool:
    """Tool for searching the web and extracting information."""
    
    def __init__(self):
        """Initialize the web search tool."""
        try:
            self.ddgs = DDGS()
        except Exception as e:
            logger.warning("Failed to initialize DDGS", error=str(e))
            self.ddgs = None
    
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search the web using DuckDuckGo.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, url, snippet
        """
        if not self.ddgs:
            logger.error("DDGS not initialized")
            return []
            
        try:
            logger.info("Searching web", query=query, max_results=max_results)
            
            results = []
            search_results = self.ddgs.text(query, max_results=max_results)
            
            for result in search_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                })
            
            logger.info("Search completed", results_count=len(results))
            return results
            
        except Exception as e:
            logger.error("Search failed", error=str(e))
            return []
    
    def search_news(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search for news articles.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of news articles
        """
        if not self.ddgs:
            logger.error("DDGS not initialized")
            return []
            
        try:
            logger.info("Searching news", query=query, max_results=max_results)
            
            results = []
            news_results = self.ddgs.news(query, max_results=max_results)
            
            for result in news_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("body", ""),
                    "date": result.get("date", ""),
                    "source": result.get("source", ""),
                })
            
            logger.info("News search completed", results_count=len(results))
            return results
            
        except Exception as e:
            logger.error("News search failed", error=str(e))
            return []
    
    def extract_page_content(self, url: str) -> Optional[str]:
        """
        Extract main content from a webpage.
        
        Args:
            url: URL to extract content from
            
        Returns:
            Extracted text content or None if failed
        """
        try:
            logger.info("Extracting page content", url=url)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit to first 2000 characters
            text = text[:2000]
            
            logger.info("Content extracted", length=len(text))
            return text
            
        except Exception as e:
            logger.error("Content extraction failed", url=url, error=str(e))
            return None


# Global instance - THIS WAS MISSING!
web_search_tool = WebSearchTool()