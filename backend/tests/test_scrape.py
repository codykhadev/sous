from pathlib import Path

import pytest

from app.services.scrape import ScrapeError, extract_recipe, normalize_url

FIXTURES = Path(__file__).parent / "fixtures"
URL = "https://myfoodblog.example/garlic-butter-pasta"


def test_extracts_recipe_from_schema_org_data() -> None:
    recipe = extract_recipe((FIXTURES / "recipe_jsonld.html").read_text(), URL)
    assert recipe.title == "Garlic Butter Pasta"
    assert recipe.source_type == "url"
    assert recipe.source_url == URL
    assert recipe.image_url == "https://example.com/images/pasta.jpg"
    assert recipe.servings == 4
    assert recipe.total_minutes == 25
    assert recipe.ingredients[0] == "12 oz spaghetti"
    assert len(recipe.ingredients) == 5
    assert recipe.steps == [
        "Boil the spaghetti in salted water for 10 minutes.",
        "Melt the butter and cook the garlic for 1 minute.",
        "Toss the pasta with the sauce and parmesan.",
    ]


def test_page_without_recipe_raises() -> None:
    with pytest.raises(ScrapeError, match="Couldn't find a recipe"):
        extract_recipe((FIXTURES / "no_recipe.html").read_text(), URL)


def test_normalize_url_drops_fragment() -> None:
    assert normalize_url("  https://a.example/pasta#recipe ") == "https://a.example/pasta"


@pytest.mark.parametrize("bad", ["pasta recipe", "ftp://a.example/x", "https://"])
def test_normalize_url_rejects_non_links(bad: str) -> None:
    with pytest.raises(ScrapeError):
        normalize_url(bad)
