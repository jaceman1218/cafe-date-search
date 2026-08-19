"""Google Maps Platform (Places API) との連携をまとめるモジュール。

将来的にキャッシュやリトライ、レート制御を追加しやすいよう、
Google Maps へのアクセスはこのモジュール経由に限定する。

GOOGLE_MAPS_API_KEY が未設定の場合は「モックモード」で動作し、
services/mock_data.py のダミーデータを返す（実際のGoogle APIは呼ばない）。
これにより、APIキーが無くても検索〜詳細画面までの動作確認ができる。

実データ利用時は services/place_cache.py 経由でSQLiteにキャッシュし、
同じエリア・同じ店舗への再アクセスではAPIを呼び直さない（詳細はそちらを参照）。
"""
from __future__ import annotations

import logging
import os
from typing import Any, Optional

import httpx

from backend.services.mock_data import get_mock_cafes, get_mock_place_detail
from backend.services.place_cache import (
    get_cached_place_detail,
    get_cached_places,
    save_place_detail_cache,
    save_places_cache,
)

logger = logging.getLogger(__name__)

PLACES_TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
PLACES_PHOTO_URL = "https://maps.googleapis.com/maps/api/place/photo"


class GoogleMapsClientError(RuntimeError):
    """Google Maps API呼び出しに関するエラー。"""


class GoogleMapsClient:
    """Google Maps Platform の Places API を呼び出す薄いクライアント。

    APIキー未設定時は mock_mode=True になり、ダミーデータを返す。
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.environ.get("GOOGLE_MAPS_API_KEY")
        self.mock_mode = not self.api_key
        if self.mock_mode:
            logger.warning(
                "GOOGLE_MAPS_API_KEY が未設定のため、モックモードで動作します"
                "（ダミーのカフェデータを返します。.envにキーを設定すると実データになります）。"
            )

    async def search_cafes(self, area: str) -> list[dict[str, Any]]:
        """指定エリア付近のカフェを検索する。

        MVPでは Text Search API を利用し、「{area} カフェ」で検索する。
        """
        if self.mock_mode:
            return get_mock_cafes(area)

        cached = get_cached_places(area)
        if cached is not None:
            logger.info("エリア「%s」はキャッシュを使用します（Google API呼び出しなし）", area)
            return cached

        params = {
            "query": f"{area} カフェ",
            "type": "cafe",
            "language": "ja",
            "key": self.api_key,
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(PLACES_TEXT_SEARCH_URL, params=params)
            response.raise_for_status()
            data = response.json()

        status = data.get("status")
        if status not in ("OK", "ZERO_RESULTS"):
            raise GoogleMapsClientError(f"Places API エラー: {status}")

        results = data.get("results", [])
        save_places_cache(area, results)
        return results

    async def get_place_details(self, place_id: str) -> dict[str, Any]:
        """店舗の詳細情報を取得する。"""
        if self.mock_mode:
            return get_mock_place_detail(place_id)

        cached = get_cached_place_detail(place_id)
        if cached is not None:
            logger.info("店舗「%s」はキャッシュを使用します（Google API呼び出しなし）", place_id)
            return cached

        fields = ",".join(
            [
                "name",
                "rating",
                "user_ratings_total",
                "price_level",
                "formatted_address",
                "formatted_phone_number",
                "opening_hours",
                "website",
                "url",
                "photo",
                "review",
            ]
        )
        params = {
            "place_id": place_id,
            "fields": fields,
            "language": "ja",
            "key": self.api_key,
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(PLACES_DETAILS_URL, params=params)
            response.raise_for_status()
            data = response.json()

        status = data.get("status")
        if status != "OK":
            raise GoogleMapsClientError(f"Places API エラー: {status}")

        result = data.get("result", {})
        save_place_detail_cache(place_id, result)
        return result

    async def get_photo_bytes(self, photo_reference: str, max_width: int = 800) -> tuple[bytes, str]:
        """店舗写真の画像本体を取得する（バイナリ, content-type）。

        APIキーをフロントエンドに渡さないよう、呼び出し側（api/places.py）で
        バックエンド経由のプロキシとして使う想定。
        """
        if self.mock_mode:
            raise GoogleMapsClientError("モックモードでは写真を取得できません")

        params = {
            "photo_reference": photo_reference,
            "maxwidth": max_width,
            "key": self.api_key,
        }
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(PLACES_PHOTO_URL, params=params)
            response.raise_for_status()

        content_type = response.headers.get("content-type", "image/jpeg")
        return response.content, content_type
