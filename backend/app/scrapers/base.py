from abc import ABC, abstractmethod
from typing import List, Dict, Any
import hashlib
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

class BaseScraper(ABC):
    source_name: str = ""
    base_url: str = ""
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def fetch_html(self, url: str) -> str:
        """Fetch raw HTML with retry logic and standard user agent."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        async with httpx.AsyncClient(timeout=30, verify=False) as client:
            response = await client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status()
            return response.text
    
    def make_url_hash(self, url: str) -> str:
        """Create a unique MD5 hash for URL deduplication."""
        normalized = url.strip().lower().rstrip("/")
        return hashlib.md5(normalized.encode()).hexdigest()
    
    @abstractmethod
    async def discover(self) -> List[Dict[str, Any]]:
        """
        Scan source for latest opportunities.
        Returns a list of dicts with:
        {
            'url': str,
            'url_hash': str,
            'raw_content': str,
            'source': str
        }
        """
        pass
