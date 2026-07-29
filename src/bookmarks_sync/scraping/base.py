"""Base types for the scraping framework."""

from dataclasses import dataclass
import re
from typing import ClassVar, Protocol


@dataclass(frozen=True)
class ScrapedContent:
    """Structured content extracted from a scraped web page."""

    source_type: str
    source_name: str | None = None
    verse_ref: str | None = None
    devanagari: str | None = None
    verse_text: str | None = None
    synonyms: list[tuple[str, str]] | None = None
    translation: str | None = None
    purport: str | None = None
    body_text: str | None = None


class Scraper(Protocol):
    """Interface all scrapers must implement."""

    pattern: ClassVar[re.Pattern]

    def scrape(self, url: str) -> ScrapedContent | None:
        """Return scraped content for *url*, or None if scraping fails."""
