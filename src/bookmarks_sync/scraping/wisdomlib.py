"""Scraper for WisdomLib.org scripture verse pages."""

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
_DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")


def _collect_text(node: Tag) -> str:
    """Collect text from a tag preserving ``<br>`` as newlines."""
    parts: list[str] = []
    for child in node.children:
        if isinstance(child, Tag):
            if child.name == "br":
                parts.append("\n")
            else:
                parts.append(_collect_text(child))
        elif isinstance(child, str):
            parts.append(child)
    return "".join(parts)


class WisdomlibScraper:
    """Scrape verse content from a WisdomLib.org page."""

    pattern: ClassVar[re.Pattern] = re.compile(r"wisdomlib\.org/hinduism/book/.+")

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

        source_name = self._extract_source_name(soup)
        verse_ref = self._extract_verse_ref(soup)

        content_div = soup.find("div", id="scontent")
        blockquote = content_div.find("blockquote") if isinstance(content_div, Tag) else None

        if not isinstance(content_div, Tag) or not isinstance(blockquote, Tag):
            return ScrapedContent(
                source_type="wisdomlib",
                source_name=source_name,
                verse_ref=verse_ref,
            )

        return ScrapedContent(
            source_type="wisdomlib",
            source_name=source_name,
            verse_ref=verse_ref,
            devanagari=self._extract_devanagari(blockquote),
            verse_text=self._extract_verse_text(blockquote),
            synonyms=self._extract_synonyms(blockquote),
            translation=self._extract_translation(content_div, blockquote),
            purport=self._extract_purport(content_div, blockquote),
        )

    # ── Section extractors ──────────────────────────────────────────────

    @staticmethod
    def _extract_source_name(soup: BeautifulSoup) -> str | None:
        """Extract the book name from <title>, <h1>, or breadcrumb."""
        title_tag = soup.find("title")
        if isinstance(title_tag, Tag):
            text = title_tag.get_text(strip=True)
            # Format: "Verse 1 [Brahma Samhita]" → "Brahma Samhita"
            m = re.search(r"\[(.+?)\]", text)
            if m:
                return m.group(1).strip() or None
            # Format: "Sri Bhakti-rasamrta-sindhu Verse 1.1.1" → book name before " Verse "
            m = re.search(r"^(.+?)\s+[Vv]erse\s", text)
            if m:
                name = m.group(1).strip()
                # Normalize: strip leading "Sri " honorific to unify with index-page titles
                if name.startswith("Sri ") or name.startswith("Śrī "):
                    name = name.split(" ", 1)[1]
                return name or None
            # Book index page: title is just the book name
            return text or None

        h1 = soup.find("h1", itemprop="name")
        if isinstance(h1, Tag):
            text = h1.get_text(strip=True)
            return text or None

        heading = soup.find("section", class_="heading")
        if isinstance(heading, Tag):
            h1 = heading.find("h1")
            if isinstance(h1, Tag):
                text = h1.get_text(strip=True)
                return text or None

        return None

    @staticmethod
    def _extract_verse_ref(soup: BeautifulSoup) -> str | None:
        title_tag = soup.find("title")
        if isinstance(title_tag, Tag):
            text = title_tag.get_text(strip=True)
            # "Verse 1 [Brahma Samhita]" → "Brahma Samhita Verse 1"
            m = re.match(r"^Verse\s+(\S+)\s+\[(.+)\]$", text)
            if m:
                return f"{m.group(2)} {m.group(1)}"
            # "Sri Bhakti-rasamrta-sindhu Verse 1.1.1" → "Verse 1.1.1"
            m = re.match(r"^.+\s+([Vv]erse\s+\S+)$", text)
            if m:
                return m.group(1)
            return text or None

        heading = soup.find("section", class_="heading")
        if isinstance(heading, Tag):
            h1 = heading.find("h1")
            if isinstance(h1, Tag):
                text = h1.get_text(strip=True)
                return text or None

        return None

    @staticmethod
    def _extract_devanagari(blockquote: Tag) -> str | None:
        # Prefer Devanagari Unicode detection over lang="sa" (often absent on Wisdomlib)
        for p in blockquote.find_all("p", recursive=False):
            if p.find("strong"):
                continue
            text = _collect_text(p).strip()
            if text and _DEVANAGARI_RE.search(text):
                return text

        p_sa = blockquote.find("p", lang="sa")
        if isinstance(p_sa, Tag):
            text = _collect_text(p_sa).strip()
            if text:
                return text

        return None

    @staticmethod
    def _extract_verse_text(blockquote: Tag) -> str | None:
        # Primary: find Devanagari <p>, get next <p> sibling with IAST text
        for p in blockquote.find_all("p", recursive=False):
            if p.find("strong"):
                continue
            text = _collect_text(p)
            if _DEVANAGARI_RE.search(text):
                nxt = p.find_next_sibling("p")
                if isinstance(nxt, Tag):
                    vtext = _collect_text(nxt).strip()
                    if vtext:
                        return vtext
                break

        # Fallback: join all <em> with IAST characters
        parts: list[str] = []
        for em in blockquote.find_all("em"):
            text = _collect_text(em).strip()
            if text and re.search(r"[īūṛṣṭñṅḍḥ]|[aeiou]\b", text):
                parts.append(text)
        return "\n\n".join(parts) if parts else None

    @staticmethod
    def _extract_synonyms(blockquote: Tag) -> list[tuple[str, str]] | None:
        entries: list[tuple[str, str]] = []

        for p_tag in blockquote.find_all("p", recursive=True):
            if p_tag.find("strong"):
                continue
            if _DEVANAGARI_RE.search(p_tag.get_text()):
                continue

            em_tags = p_tag.find_all("em")
            if not em_tags:
                continue

            has_dash = False
            for em in em_tags:
                tail = (em.next_sibling or "").strip() if isinstance(em.next_sibling, str) else ""
                if tail and tail.startswith("—"):
                    has_dash = True
                    break
                nxt = em.next_sibling
                if isinstance(nxt, str) and nxt.strip().startswith("—"):
                    has_dash = True
                    break

            if not has_dash:
                continue

            for em in em_tags:
                word = em.get_text(strip=True).rstrip(";")
                meaning_parts: list[str] = []
                after = em.next_sibling
                if isinstance(after, str):
                    cleaned = after.lstrip("—").strip()
                    if cleaned:
                        meaning_parts.append(cleaned)
                for sibling in em.find_next_siblings():
                    if sibling.name == "em":
                        break
                    if isinstance(sibling, str):
                        cleaned = sibling.replace(";", "").strip()
                        if cleaned:
                            meaning_parts.append(cleaned)
                    elif isinstance(sibling, Tag):
                        txt = sibling.get_text(strip=True)
                        if txt:
                            meaning_parts.append(txt)

                meaning = " ".join(meaning_parts).strip().rstrip(";").strip()
                if meaning.startswith("\u201c") or meaning.startswith("\u2018") or meaning.startswith('"'):
                    break
                if word and meaning:
                    entries.append((word, meaning))

            if entries:
                break

        return entries if entries else None

    @staticmethod
    def _extract_translation(content_div: Tag, blockquote: Tag) -> str | None:
        for p_tag in blockquote.find_all("p", recursive=True):
            text = p_tag.get_text()
            if text.strip() and (text.strip().startswith("\u201c") or text.strip().startswith("\u2018") or text.strip().startswith('"')):
                return " ".join(text.split())

        h2 = content_div.find("h2")
        if isinstance(h2, Tag) and "translation" in h2.get_text(strip=True).lower():
            translations: list[str] = []
            cursor = h2
            while True:
                cursor = cursor.find_next_sibling()
                if cursor is None:
                    break
                if cursor.name in ("h2", "h3", "hr", "footer", "nav"):
                    break
                if cursor.name == "p":
                    text = " ".join(cursor.get_text().split())
                    if text and not cursor.find("strong"):
                        translations.append(text)
            if translations:
                return "\n\n".join(translations)

        return None

    @staticmethod
    def _extract_purport(content_div: Tag, blockquote: Tag) -> str | None:
        paragraphs: list[str] = []
        for heading in content_div.find_all("h2"):
            heading_text = heading.get_text(strip=True).lower()
            if "commentary" not in heading_text and "purport" not in heading_text:
                continue
            cursor = heading
            while True:
                nxt = cursor.find_next_sibling()
                if nxt is None:
                    break
                if nxt.name in ("h2", "h3", "hr", "footer", "nav"):
                    break
                if nxt.name == "p":
                    text = nxt.get_text(strip=True)
                    if text:
                        paragraphs.append(text)
                cursor = nxt

        result = "\n\n".join(paragraphs)
        return result or None
