"""Scraper for Vedabase.io Bhagavad-gītā and Śrīmad-Bhāgavatam verses."""

from __future__ import annotations

import logging
import re
from typing import ClassVar

import requests
from bs4 import BeautifulSoup, Tag

from bookmarks_sync.scraping.base import ScrapedContent, Scraper

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}
_TIMEOUT = 15


class VedabaseScraper:
    """Scrape verse content from a Vedabase.io page."""

    pattern: ClassVar[re.Pattern] = re.compile(r"vedabase\.io/en/library/.+")

    def scrape(self, url: str) -> ScrapedContent | None:
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
            resp.raise_for_status()
        except Exception:
            logger.warning("Failed to fetch %s", url, exc_info=True)
            return None

        try:
            soup = BeautifulSoup(resp.text, "html.parser")
        except Exception:
            logger.warning("Failed to parse HTML from %s", url, exc_info=True)
            return None

        main = soup.find("main")
        if not isinstance(main, Tag):
            logger.warning("No <main> tag found on %s", url)
            return None

        return ScrapedContent(
            source_type="vedabase",
            source_name=self._extract_source_name(soup),
            verse_ref=self._extract_verse_ref(main),
            devanagari=self._extract_devanagari(main),
            verse_text=self._extract_verse_text(main),
            synonyms=self._extract_synonyms(main),
            translation=self._extract_translation(main),
            purport=self._extract_purport(main),
            body_text=self._extract_body_text(main),
        )

    # ── Section extractors ──────────────────────────────────────────────

    @staticmethod
    def _extract_source_name(soup: BeautifulSoup) -> str | None:
        """Extract the book title from the breadcrumb navigation.

        The breadcrumb has the structure: Library » Book Title » Chapter ...
        We want the second item (index 1).
        """
        nav = soup.find("nav", attrs={"aria-label": "Breadcrumb"})
        if not isinstance(nav, Tag):
            return None
        ol = nav.find("ol")
        if not isinstance(ol, Tag):
            return None
        links = ol.find_all("a")
        if len(links) >= 2:
            text = links[1].get_text(strip=True)
            return text or None
        return None

    @staticmethod
    def _extract_verse_ref(main: Tag) -> str | None:
        h1 = main.find("h1")
        if isinstance(h1, Tag):
            text = h1.get_text(strip=True)
            return text or None
        return None

    @staticmethod
    def _extract_devanagari(main: Tag) -> str | None:
        wrapper = main.find("div", class_="av-devanagari")
        if not isinstance(wrapper, Tag):
            return None
        # Prefer the large-text inner div, fall back to wrapper text
        inner = wrapper.find("div", class_="em-text-lg")
        if isinstance(inner, Tag):
            text = inner.get_text(strip=True)
        else:
            text = wrapper.get_text(strip=True)
        # Strip the hidden "Devanagari" heading label if it leaked through
        for tag in wrapper.find_all(["h2", "h3", "h4"]):
            label = tag.get_text(strip=True)
            if label and text.startswith(label):
                text = text[len(label) :].strip()
                break
        return text or None

    @staticmethod
    def _extract_verse_text(main: Tag) -> str | None:
        wrapper = main.find("div", class_="av-verse_text")
        if not isinstance(wrapper, Tag):
            return None
        em = wrapper.find("em")
        if isinstance(em, Tag):
            # Preserve <br/> as newlines
            parts: list[str] = []
            for child in em.children:
                if isinstance(child, Tag) and child.name == "br":
                    parts.append("\n")
                elif isinstance(child, Tag):
                    parts.append(child.get_text(strip=True))
                elif isinstance(child, str):
                    parts.append(child.strip())
            text = "".join(parts).strip()
            return text or None
        # Fallback: just get the wrapper text
        text = wrapper.get_text(strip=True)
        return text or None

    @staticmethod
    def _extract_synonyms(main: Tag) -> list[tuple[str, str]] | None:
        wrapper = main.find("div", class_="av-synonyms")
        if not isinstance(wrapper, Tag):
            return None
        entries: list[tuple[str, str]] = []
        for span in wrapper.find_all("span", class_="inline", recursive=True):
            a_tag = span.find("a")
            if not isinstance(a_tag, Tag):
                continue
            em_tag = a_tag.find("em")
            sanskrit = (em_tag.get_text(strip=True) if isinstance(em_tag, Tag) else a_tag.get_text(strip=True)).strip().rstrip(";")
            # The meaning follows the <a> tag, separated by an em-dash
            meaning_parts: list[str] = []
            for sibling in a_tag.next_siblings:
                if isinstance(sibling, Tag) and sibling.name == "span":
                    meaning_parts.append(sibling.get_text(strip=True))
                elif isinstance(sibling, str):
                    # Skip the em-dash separator and semicolons
                    cleaned = sibling.replace("—", "").replace(";", "").strip()
                    if cleaned:
                        meaning_parts.append(cleaned)
            meaning = " ".join(meaning_parts).strip().rstrip(";").strip()
            if sanskrit and meaning:
                entries.append((sanskrit, meaning))
        return entries if entries else None

    @staticmethod
    def _extract_translation(main: Tag) -> str | None:
        wrapper = main.find("div", class_="av-translation")
        if not isinstance(wrapper, Tag):
            return None
        strong = wrapper.find("strong")
        if isinstance(strong, Tag):
            text = strong.get_text(strip=True)
            return text or None
        text = wrapper.get_text(strip=True)
        return text or None

    @staticmethod
    def _extract_purport(main: Tag) -> str | None:
        wrapper = main.find("div", class_="av-purport")
        if not isinstance(wrapper, Tag):
            return None
        paragraphs: list[str] = []
        for child in wrapper.find_all("div", recursive=True):
            # Skip heading tags
            if child.name in ("h2", "h3", "h4"):
                continue
            text = child.get_text(strip=True)
            if text:
                paragraphs.append(text)
        result = "\n\n".join(paragraphs)
        return result or None

    @staticmethod
    def _extract_body_text(main: Tag) -> str | None:
        """Extract full body text for non-verse pages (letters, transcripts)."""
        copy_divs = main.find_all("div", class_="copy")
        if not copy_divs:
            return None
        # Skip the first copy div (h1 title) — already in verse_ref
        paragraphs: list[str] = []
        for div in copy_divs[1:]:
            text = div.get_text(strip=True)
            if text:
                paragraphs.append(text)
        result = "\n\n".join(paragraphs)
        return result or None
