import feedparser
from app.scrapers.base import BaseScraper
from loguru import logger

RSS_FEEDS = [
    {"name": "youth_opportunities", "url": "https://youthop.com/feed"},
    {"name": "opportunity_portal", "url": "https://www.opportunityportal.info/feed/"}
]

class RSSFeedScraper(BaseScraper):
    source_name = "rss_feeds"
    
    async def discover(self):
        results = []
        for feed_info in RSS_FEEDS:
            feed_name = feed_info["name"]
            feed_url = feed_info["url"]
            logger.info(f"Parsing feed: {feed_name} from {feed_url}")
            try:
                # Use standard client to fetch XML content first to leverage user agents & SSL verify rules
                xml_data = await self.fetch_html(feed_url)
                feed = feedparser.parse(xml_data)
                
                for entry in feed.entries[:8]:
                    url = entry.get("link", "")
                    if not url:
                        continue
                    
                    title = entry.get("title", "")
                    summary = entry.get("summary", "")
                    published = entry.get("published", "")
                    
                    content_block = f"""
                    Source Feed: {feed_name}
                    Title: {title}
                    Published: {published}
                    Summary: {summary}
                    """
                    
                    results.append({
                        "url": url,
                        "url_hash": self.make_url_hash(url),
                        "raw_content": content_block,
                        "source": f"rss_{feed_name}"
                    })
            except Exception as e:
                logger.warning(f"Failed parsing feed {feed_name}: {e}")
                
        return results
