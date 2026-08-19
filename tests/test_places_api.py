"""api/places.py の統合テスト（モックモード前提）。"""
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_search_returns_mock_results(monkeypatch):
    monkeypatch.delenv("GOOGLE_MAPS_API_KEY", raising=False)
    response = client.post(
        "/api/places/search",
        json={"areas": ["梅田"], "time_slot": "day", "budget": "under_3000"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 10


def test_photo_not_found_in_mock_mode(monkeypatch):
    """モックモードには写真データが無いので、写真エンドポイントは404を返す。"""
    monkeypatch.delenv("GOOGLE_MAPS_API_KEY", raising=False)
    response = client.get("/api/places/mock-place-1/photo")
    assert response.status_code == 404
