from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.frontend import mount_frontend


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "app.js").write_text("console.log('sous')")
    (tmp_path / "index.html").write_text("<div id=root></div>")
    (tmp_path / "favicon.svg").write_text("<svg/>")
    app = FastAPI()

    @app.get("/api/ping")
    def ping() -> dict[str, str]:
        return {"pong": "yes"}

    mount_frontend(app, tmp_path)
    return TestClient(app)


def test_api_routes_still_work(client: TestClient) -> None:
    assert client.get("/api/ping").json() == {"pong": "yes"}


def test_unknown_api_path_is_404_not_index(client: TestClient) -> None:
    assert client.get("/api/nope").status_code == 404


def test_client_route_falls_back_to_index(client: TestClient) -> None:
    res = client.get("/recipes/42/cook")
    assert res.status_code == 200
    assert "id=root" in res.text


def test_static_files_served(client: TestClient) -> None:
    assert client.get("/assets/app.js").text == "console.log('sous')"
    assert client.get("/favicon.svg").text == "<svg/>"


def test_path_traversal_returns_index(client: TestClient) -> None:
    res = client.get("/..%2F..%2Fetc%2Fpasswd")
    assert "id=root" in res.text
