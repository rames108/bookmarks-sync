"""Web scraping support for enriched bookmark capture."""

from bookmarks_sync.scraping.base import ScrapedContent
from bookmarks_sync.scraping.registry import scrape, register

__all__ = ["ScrapedContent", "scrape", "register"]
