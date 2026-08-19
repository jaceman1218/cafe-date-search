"""GOOGLE_MAPS_API_KEY未設定時のモックモード動作を確認するテスト。"""
import asyncio

from backend.services.google_maps import GoogleMapsClient


def test_mock_mode_when_no_api_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_MAPS_API_KEY", raising=False)

    client = GoogleMapsClient()
    assert client.mock_mode is True

    places = asyncio.run(client.search_cafes("梅田"))
    assert len(places) > 0
    assert "place_id" in places[0]

    detail = asyncio.run(client.get_place_details(places[0]["place_id"]))
    assert detail["place_id"] == places[0]["place_id"]


def test_real_mode_when_api_key_present(monkeypatch):
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "dummy-key")

    client = GoogleMapsClient()
    assert client.mock_mode is False
