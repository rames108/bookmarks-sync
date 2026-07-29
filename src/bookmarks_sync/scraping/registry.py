"""URL-pattern-based scraper registry and dispatcher."""

import logging
from typing import NoReturn

from bookmarks_sync.scraping.base import ScrapedContent, Scraper

logger = logging.getLogger(__name__)

_scrapers: list[Scraper] = []


def register(scraper: Scraper) -> None:
    """Register a scraper instance."""
    _scrapers.append(scraper)


def scrape(url: str) -> ScrapedContent | None:
    """Iterate registered scrapers and return the first successful result."""
    for scraper in _scrapers:
        if scraper.pattern.search(url):
            try:
                result = scraper.scrape(url)
                if result is not None:
                    return result
            except Exception:
                logger.warning("Scraper %s failed for %s", type(scraper).__name__, url, exc_info=True)
    return None


# ── Auto-register known scrapers ──────────────────────────────────────────

def _auto_register() -> None:
    try:
        from bookmarks_sync.scraping.vedabase import VedabaseScraper

        register(VedabaseScraper())
    except ImportError:
        logger.debug("VedabaseScraper not available (missing deps?)")

    try:
        from bookmarks_sync.scraping.wisdomlib import WisdomlibScraper

        register(WisdomlibScraper())
    except ImportError:
        logger.debug("WisdomlibScraper not available (missing deps?)")


_auto_register()
