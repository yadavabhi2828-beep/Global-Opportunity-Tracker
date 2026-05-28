from app.scrapers.opportunity_desk import OpportunityDeskScraper
from app.scrapers.rss_scraper import RSSFeedScraper

ALL_SCRAPERS = [
    OpportunityDeskScraper(),
    RSSFeedScraper()
]

__all__ = ["OpportunityDeskScraper", "RSSFeedScraper", "ALL_SCRAPERS"]
