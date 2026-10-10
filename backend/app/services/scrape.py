import re
from collections.abc import Callable
from typing import TypeVar
from urllib.parse import urldefrag, urlparse

import httpx2
from recipe_scrapers import scrape_html
from recipe_scrapers._exceptions import RecipeScrapersExceptions

from ..schemas import RecipeIn

T = TypeVar("T")

# A browser User-Agent gets blocked more often: bot protection sees it doesn't match the connection.
HEADERS = {
    "User-Agent": "Sous/0.1 (personal recipe app)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}


class ScrapeError(Exception):
    pass


def normalize_url(url: str) -> str:
    url = urldefrag(url.strip()).url
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ScrapeError("That doesn't look like a web link. It should start with http:// or https://.")
    return url


def fetch_html(url: str) -> str:
    try:
        res = httpx2.get(url, headers=HEADERS, follow_redirects=True, timeout=15)
    except httpx2.TimeoutException as exc:
        raise ScrapeError("The site took too long to respond.") from exc
    except httpx2.HTTPError as exc:
        raise ScrapeError("Couldn't reach that site. Check the link and your connection.") from exc
    if res.status_code in (401, 402, 403, 429):
        raise ScrapeError(
            f"This site blocks apps from reading its pages (HTTP {res.status_code}). Try adding the recipe manually."
        )
    if res.status_code >= 400:
        raise ScrapeError(f"The site returned an error (HTTP {res.status_code}).")
    return res.text


def _optional(read: Callable[[], T]) -> T | None:
    try:
        return read()
    except (RecipeScrapersExceptions, AttributeError, TypeError, ValueError, KeyError, IndexError):
        return None


def _servings(yields: str | None) -> int | None:
    match = re.search(r"\d+", yields or "")
    return int(match.group()) if match else None


def _section_names(scraper) -> set[str]:
    data = getattr(getattr(scraper, "schema", None), "data", None) or {}
    instructions = data.get("recipeInstructions") or []
    if isinstance(instructions, dict):
        instructions = [instructions]
    return {
        item["name"].strip()
        for item in instructions
        if isinstance(item, dict) and item.get("@type") == "HowToSection" and isinstance(item.get("name"), str)
    }


def _steps(scraper) -> list[str]:
    steps = _optional(scraper.instructions_list) or []
    if not steps:
        steps = (_optional(scraper.instructions) or "").split("\n")
    # recipe-scrapers returns section headings ("For the sauce") as if they were steps.
    sections = _section_names(scraper)
    return [s.strip() for s in steps if s.strip() and s.strip() not in sections]


def extract_recipe(html: str, url: str) -> RecipeIn:
    try:
        scraper = scrape_html(html, org_url=url, supported_only=False)
    except RecipeScrapersExceptions as exc:
        raise ScrapeError("Couldn't find a recipe on that page.") from exc

    title = _optional(scraper.title)
    ingredients = [i.strip() for i in _optional(scraper.ingredients) or [] if i.strip()]
    if not title or not ingredients:
        raise ScrapeError("Couldn't find a recipe on that page.")

    total = _optional(scraper.total_time)
    return RecipeIn(
        title=title.strip(),
        source_type="url",
        source_url=url,
        image_url=_optional(scraper.image) or None,
        servings=_servings(_optional(scraper.yields)),
        total_minutes=int(total) if isinstance(total, (int, float)) and total > 0 else None,
        ingredients=ingredients,
        steps=_steps(scraper),
    )


def scrape_recipe(url: str) -> RecipeIn:
    return extract_recipe(fetch_html(url), url)
