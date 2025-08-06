"""
Thread Generation Service using OpenAI
Handles content-to-thread conversion with smart splitting
"""

import os
import re
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ThreadGeneratorService:
    """Service for generating Twitter/X threads from content"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OpenAI API key not found - thread generation will be limited")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized successfully")
        
        # Configuration
        self.max_tweet_length = int(os.getenv("MAX_TWEET_LENGTH", "280"))
        self.max_content_length = int(os.getenv("MAX_CONTENT_LENGTH", "10000"))
        
        # Allowed domains for URL scraping
        self.allowed_domains = self._parse_allowed_domains()
    
    def _parse_allowed_domains(self) -> List[str]:
        """Parse allowed domains from environment variable"""
        domains_str = os.getenv("ALLOWED_DOMAINS", "")
        if not domains_str:
            # Default allowed domains
            return [
                "medium.com", "*.medium.com",
                "dev.to", "*.dev.to",
                "substack.com", "*.substack.com",
                "hashnode.com", "*.hashnode.com",
                "github.com", "*.github.com"
            ]
        return [d.strip() for d in domains_str.split(",")]
    
    def _is_domain_allowed(self, url: str) -> bool:
        """Check if URL domain is in allowed list"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        for allowed in self.allowed_domains:
            if allowed.startswith("*."):
                # Wildcard subdomain
                base = allowed[2:]
                if domain == base or domain.endswith(f".{base}"):
                    return True
            elif domain == allowed:
                return True
        return False
    
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape content from URL"""
        try:
            # Check if domain is allowed
            if not self._is_domain_allowed(url):
                return {
                    "success": False,
                    "error": f"Domain not allowed. Supported domains: {', '.join(self.allowed_domains)}"
                }
            
            # Fetch content
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                response = await client.get(url, headers=headers)
                response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = ""
            if soup.title:
                title = soup.title.string
            elif soup.find('h1'):
                title = soup.find('h1').get_text()
            
            # Extract content
            # Try different content selectors
            content = ""
            
            # Try article tag first
            article = soup.find('article')
            if article:
                content = article.get_text()
            else:
                # Try main tag
                main = soup.find('main')
                if main:
                    content = main.get_text()
                else:
                    # Fallback to body
                    body = soup.find('body')
                    if body:
                        # Remove script and style elements
                        for script in body(["script", "style"]):
                            script.decompose()
                        content = body.get_text()
            
            # Clean up content
            content = re.sub(r'\s+', ' ', content).strip()
            
            # Limit content length
            if len(content) > self.max_content_length:
                content = content[:self.max_content_length] + "..."
            
            return {
                "success": True,
                "title": title,
                "content": content,
                "url": url
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error scraping URL {url}: {e}")
            return {"success": False, "error": f"Failed to fetch URL: {e.response.status_code}"}
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_thread(self, content: str, url: Optional[str] = None) -> Dict[str, Any]:
        """Generate thread from content using OpenAI"""
        try:
            # If URL provided, scrape it first
            if url and url.startswith("http"):
                scrape_result = await self.scrape_url(url)
                if not scrape_result["success"]:
                    return scrape_result
                content = scrape_result.get("content", content)
                title = scrape_result.get("title", "")
            else:
                title = ""
            
            # Limit content length
            if len(content) > self.max_content_length:
                content = content[:self.max_content_length]
            
            # If no OpenAI client, use simple splitting
            if not self.client:
                tweets = self._simple_split(content)
                return {
                    "success": True,
                    "tweets": tweets,
                    "thread_count": len(tweets),
                    "title": title,
                    "method": "simple_split"
                }
            
            # Use OpenAI to generate thread
            prompt = f"""Convert the following content into a Twitter/X thread. 
Each tweet should be under {self.max_tweet_length} characters.
Make the thread engaging and informative.
Number each tweet (1/, 2/, etc.) except the last one.
Include relevant hashtags where appropriate.

Content:
{content}"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at creating engaging Twitter/X threads from articles and content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse the response into tweets
            thread_text = response.choices[0].message.content
            tweets = self._parse_thread(thread_text)
            
            return {
                "success": True,
                "tweets": tweets,
                "thread_count": len(tweets),
                "title": title,
                "method": "openai_generated"
            }
            
        except Exception as e:
            logger.error(f"Error generating thread: {e}")
            # Fallback to simple splitting
            tweets = self._simple_split(content)
            return {
                "success": True,
                "tweets": tweets,
                "thread_count": len(tweets),
                "error": str(e),
                "method": "fallback_split"
            }
    
    def _simple_split(self, content: str) -> List[str]:
        """Simple method to split content into tweets"""
        words = content.split()
        tweets = []
        current_tweet = []
        current_length = 0
        tweet_num = 1
        
        for word in words:
            # Account for the numbering (e.g., "1/ ")
            prefix_length = len(f"{tweet_num}/ ")
            
            if current_length + len(word) + 1 + prefix_length > self.max_tweet_length:
                # Finish current tweet
                if current_tweet:
                    tweet_text = f"{tweet_num}/ " + " ".join(current_tweet)
                    tweets.append(tweet_text)
                    tweet_num += 1
                    current_tweet = [word]
                    current_length = len(word)
            else:
                current_tweet.append(word)
                current_length += len(word) + 1
        
        # Add last tweet
        if current_tweet:
            if tweet_num > 1:
                # Last tweet doesn't need numbering
                tweets.append(" ".join(current_tweet))
            else:
                # Single tweet
                tweets.append(" ".join(current_tweet))
        
        # Limit to 25 tweets max
        return tweets[:25]
    
    def _parse_thread(self, thread_text: str) -> List[str]:
        """Parse OpenAI response into individual tweets"""
        # Split by common patterns
        lines = thread_text.split('\n')
        tweets = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Remove markdown formatting
            line = re.sub(r'\*\*(.+?)\*\*', r'\1', line)  # Bold
            line = re.sub(r'\*(.+?)\*', r'\1', line)  # Italic
            
            # Check if it's a numbered tweet
            if re.match(r'^\d+[/.)]', line):
                tweets.append(line)
            elif len(line) <= self.max_tweet_length:
                tweets.append(line)
            else:
                # Split long lines
                split_tweets = self._simple_split(line)
                tweets.extend(split_tweets)
        
        # Ensure tweets are within character limit
        valid_tweets = []
        for tweet in tweets:
            if len(tweet) <= self.max_tweet_length:
                valid_tweets.append(tweet)
            else:
                # Truncate if needed
                valid_tweets.append(tweet[:self.max_tweet_length-3] + "...")
        
        return valid_tweets[:25]  # Max 25 tweets

# Singleton instance
thread_generator = ThreadGeneratorService()