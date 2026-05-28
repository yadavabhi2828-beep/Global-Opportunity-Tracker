from app.scrapers.base import BaseScraper
from bs4 import BeautifulSoup
import feedparser
from loguru import logger

class OpportunityDeskScraper(BaseScraper):
    source_name = "opportunity_desk"
    base_url = "https://opportunitydesk.org"
    
    async def discover(self):
        results = []
        feed_url = f"{self.base_url}/feed/"
        
        try:
            logger.info(f"Fetching RSS feed from {feed_url}")
            # Fetch RSS XML content
            xml_data = await self.fetch_html(feed_url)
            feed = feedparser.parse(xml_data)
            
            # Read first 10 entries to stay within rate-limits and avoid hammering
            for entry in feed.entries[:10]:
                url = entry.get("link")
                if not url:
                    continue
                
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                
                logger.info(f"Discovered Opportunity Desk link: {url}")
                
                raw_text = ""
                # Attempt to load full page content
                try:
                    page_html = await self.fetch_html(url)
                    page_soup = BeautifulSoup(page_html, "html.parser")
                    
                    content_div = page_soup.find("div", class_="entry-content")
                    if content_div:
                        raw_text = content_div.get_text(separator="\n")
                    else:
                        raw_text = page_soup.get_text(separator="\n")
                except Exception as ex:
                    logger.warning(f"Could not fetch full content for {url}: {ex}. Falling back to summary.")
                    raw_text = f"Title: {title}\nSummary: {summary}"
                
                results.append({
                    "url": url,
                    "url_hash": self.make_url_hash(url),
                    "raw_content": f"Title: {title}\nSummary: {summary}\n\nFull Details:\n{raw_text}",
                    "source": self.source_name
                })
        except Exception as e:
            logger.error(f"OpportunityDeskScraper failed: {e}")
            
        return results
