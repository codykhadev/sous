import pytest
from fastapi.testclient import TestClient

from app.schemas import RecipeIn
from app.services import scrape

PASTA = {
    "title": "Garlic Butter Pasta",
    "source_type": "url",
    "source_url": "https://blog.example/pasta",
    "servings": 4,
    "total_minutes": 25,
    "tags": ["Dinner", " quick ", "dinner", ""],
    "ingredients": ["12 oz spaghetti", "", "2-3 cloves garlic, minced"],
    "steps": ["Boil the pasta.", "  ", "Add the garlic."],
}


def create(client: TestClient, **overrides) -> dict:
    res = client.post("/api/recipes", json={**PASTA, **overrides})
    assert res.status_code == 201, res.text
    return res.json()


def test_create_parses_ingredients_and_cleans_input(client: TestClient) -> None:
    recipe = create(client)
    assert recipe["tags"] == ["dinner", "quick"]
    assert [s["text"] for s in recipe["steps"]] == ["Boil the pasta.", "Add the garlic."]
    garlic = recipe["ingredients"][1]
    assert garlic["raw"] == "2-3 cloves garlic, minced"
    assert garlic["position"] == 1
    assert (garlic["quantity"], garlic["quantity_max"], garlic["unit"], garlic["name"], garlic["note"]) == (
        2, 3, "clove", "garlic", "minced"
    )


def test_create_rejects_blank_title(client: TestClient) -> None:
    assert client.post("/api/recipes", json={**PASTA, "title": "   "}).status_code == 422


def test_get_and_404(client: TestClient) -> None:
    recipe = create(client)
    assert client.get(f"/api/recipes/{recipe['id']}").json()["title"] == "Garlic Butter Pasta"
    assert client.get("/api/recipes/999999").status_code == 404


def test_update_replaces_ingredients_and_steps(client: TestClient) -> None:
    recipe = create(client)
    res = client.put(
        f"/api/recipes/{recipe['id']}",
        json={**PASTA, "title": "Lemon Pasta", "ingredients": ["1 lemon"], "steps": ["Zest it."]},
    )
    assert res.status_code == 200
    updated = res.json()
    assert updated["title"] == "Lemon Pasta"
    assert [i["raw"] for i in updated["ingredients"]] == ["1 lemon"]
    assert [s["text"] for s in updated["steps"]] == ["Zest it."]


def test_delete(client: TestClient) -> None:
    recipe = create(client)
    assert client.delete(f"/api/recipes/{recipe['id']}").status_code == 204
    assert client.get(f"/api/recipes/{recipe['id']}").status_code == 404
    assert client.delete(f"/api/recipes/{recipe['id']}").status_code == 404


def test_list_search_and_tag_filter(client: TestClient) -> None:
    create(client)
    create(client, title="Pancakes", tags=["breakfast"], ingredients=["2 cups flour", "1 egg"], source_url=None)

    titles = lambda params: [r["title"] for r in client.get("/api/recipes", params=params).json()]
    assert titles({}) == ["Pancakes", "Garlic Butter Pasta"]
    assert titles({"q": "pasta"}) == ["Garlic Butter Pasta"]
    assert titles({"q": "FLOUR"}) == ["Pancakes"]
    assert titles({"tag": "breakfast"}) == ["Pancakes"]
    assert titles({"q": "pasta", "tag": "breakfast"}) == []


def test_list_tags(client: TestClient) -> None:
    create(client)
    create(client, title="Pancakes", tags=["breakfast", "quick"], source_url=None)
    assert client.get("/api/recipes/tags").json() == ["breakfast", "dinner", "quick"]


def test_parse_preview(client: TestClient) -> None:
    res = client.post("/api/ingredients/parse", json={"lines": ["1 ½ cups milk", "salt to taste"]})
    assert res.json() == [
        {"raw": "1 ½ cups milk", "quantity": 1.5, "quantity_max": None, "unit": "cup", "name": "milk", "note": None},
        {"raw": "salt to taste", "quantity": None, "quantity_max": None, "unit": None, "name": "salt", "note": "to taste"},
    ]


def test_import_returns_unsaved_draft(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        scrape, "scrape_recipe", lambda url: RecipeIn(title="Soup", source_type="url", source_url=url, ingredients=["1 onion"])
    )
    res = client.post("/api/import/url", json={"url": "https://soup.example/soup#recipe"})
    assert res.status_code == 200
    assert res.json()["title"] == "Soup"
    assert res.json()["source_url"] == "https://soup.example/soup"
    assert client.get("/api/recipes").json() == []


def test_import_duplicate_url_points_to_existing(client: TestClient) -> None:
    recipe = create(client)
    res = client.post("/api/import/url", json={"url": "https://blog.example/pasta"})
    assert res.status_code == 409
    assert res.json()["detail"]["recipe_id"] == recipe["id"]


def test_import_failure_is_a_friendly_error(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(url: str) -> RecipeIn:
        raise scrape.ScrapeError("Couldn't find a recipe on that page.")

    monkeypatch.setattr(scrape, "scrape_recipe", fail)
    res = client.post("/api/import/url", json={"url": "https://blog.example/about"})
    assert res.status_code == 422
    assert res.json()["detail"]["message"] == "Couldn't find a recipe on that page."
