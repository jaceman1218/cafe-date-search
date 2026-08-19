"""店舗情報に関するスキーマ定義。"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class PlaceSummary(BaseModel):
    """検索結果一覧・カードに表示する店舗情報。"""

    place_id: str
    name: str
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    price_level: Optional[int] = None
    address: Optional[str] = None
    area: str  # この店舗がヒットした検索エリア
    distance_text: Optional[str] = None  # 例：「梅田駅から徒歩5分」。取得できない場合はNone
    opening_hours_text: Optional[str] = None
    is_open_in_time_slot: Optional[bool] = None
    google_maps_url: str
    score: float = 0.0


class PlaceDetail(PlaceSummary):
    """店舗詳細画面に表示する情報。

    写真は GET /api/places/{place_id}/photo （バックエンド経由のプロキシ）から
    取得する想定のため、ここにはURLを持たせない。フロントエンドは常にこの
    エンドポイントを叩き、404なら「写真なし」として扱う。
    """

    formatted_phone_number: Optional[str] = None
    website: Optional[str] = None
    reviews_preview: List[str] = []


class SearchResponse(BaseModel):
    """検索結果全体。"""

    results: List[PlaceSummary]
    searched_areas: List[str]
