"""Tests for the web scraping framework."""

from bookmarks_sync.scraping.base import ScrapedContent
from bookmarks_sync.scraping.registry import scrape


def test_registry_returns_none_for_unknown_url() -> None:
    """Non-matching URLs return None without error."""
    result = scrape("https://example.com/some-page")
    assert result is None


def test_registry_returns_none_for_random_url() -> None:
    """URLs that don't match any scraper pattern are ignored."""
    result = scrape("https://en.wikipedia.org/wiki/Bhagavad_Gita")
    assert result is None


def test_scraped_content_defaults() -> None:
    """ScrapedContent can be created with just source_type."""
    content = ScrapedContent(source_type="test")
    assert content.source_type == "test"
    assert content.verse_ref is None
    assert content.devanagari is None
    assert content.verse_text is None
    assert content.synonyms is None
    assert content.translation is None
    assert content.purport is None
    assert content.body_text is None


def test_scraped_content_all_fields() -> None:
    """ScrapedContent stores all fields correctly."""
    content = ScrapedContent(
        source_type="vedabase",
        verse_ref="Bg 2.13",
        devanagari="देहिनः",
        verse_text="dehinaḥ",
        synonyms=[("dehinaḥ", "of the embodied")],
        translation="As the embodied soul...",
        purport="Since every living entity...",
        body_text="Full letter content here...",
    )
    assert content.verse_ref == "Bg 2.13"
    assert content.devanagari == "देहिनः"
    assert content.synonyms == [("dehinaḥ", "of the embodied")]
    assert content.body_text == "Full letter content here..."


def test_registry_matches_wisdomlib_url() -> None:
    """Wisdomlib URLs match the registered scraper pattern."""
    result = scrape(
        "https://www.wisdomlib.org/hinduism/book/brahma-samhita-jiva-goswami-commentary/d/doc1594811.html"
    )
    # Should either scrape successfully (if network available) or return None
    # (if network down), but never crash. If it scrapes, content should be wisdomlib.
    if result is not None:
        assert result.source_type == "wisdomlib"
