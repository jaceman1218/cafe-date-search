"""Google Places検索結果・店舗詳細のSQLiteキャッシュ層。

同じエリア・同じ店舗への繰り返しアクセスでGoogle APIを毎回呼ばずに済むように、
生のAPIレスポンスをエリア名／place_id単位でSQLiteに保存する。
キャッシュはTTL（環境変数 CACHE_TTL_HOURS、デフォルト24時間）を過ぎると無効になり、
次回アクセス時に実際のAPIを呼び直して上書き保存する。

呼び出し側（google_maps.py）はこのモジュールの関数を呼ぶだけでよく、
DBの中身（テーブル構造）を意識する必要はない。
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from backend.database.session import SessionLocal
from backend.models.cache import CachedAreaSearch, CachedPlaceDetail, CachedPlacePhoto

CACHE_TTL_HOURS = float(os.environ.get("CACHE_TTL_HOURS", "24"))


def _is_fresh(fetched_at: datetime) -> bool:
    fetched_at_utc = fetched_at if fetched_at.tzinfo else fetched_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - fetched_at_utc <= timedelta(hours=CACHE_TTL_HOURS)


def get_cached_places(area: str) -> Optional[list[dict[str, Any]]]:
    """有効なキャッシュがあればエリアのカフェ一覧（生レスポンス）を返す。無ければNone。"""
    normalized = area.strip()
    with SessionLocal() as session:
        row = session.query(CachedAreaSearch).filter_by(area=normalized).one_or_none()
        if row is None or not _is_fresh(row.fetched_at):
            return None
        return json.loads(row.payload_json)


def save_places_cache(area: str, places: list[dict[str, Any]]) -> None:
    """エリアの検索結果をキャッシュに保存する（既存があれば上書き）。"""
    normalized = area.strip()
    payload = json.dumps(places, ensure_ascii=False)
    now = datetime.now(timezone.utc)
    with SessionLocal() as session:
        row = session.query(CachedAreaSearch).filter_by(area=normalized).one_or_none()
        if row is None:
            row = CachedAreaSearch(area=normalized, payload_json=payload, fetched_at=now)
            session.add(row)
        else:
            row.payload_json = payload
            row.fetched_at = now
        session.commit()


def get_cached_place_detail(place_id: str) -> Optional[dict[str, Any]]:
    """有効なキャッシュがあれば店舗詳細（生レスポンス）を返す。無ければNone。"""
    with SessionLocal() as session:
        row = session.query(CachedPlaceDetail).filter_by(place_id=place_id).one_or_none()
        if row is None or not _is_fresh(row.fetched_at):
            return None
        return json.loads(row.payload_json)


def save_place_detail_cache(place_id: str, detail: dict[str, Any]) -> None:
    """店舗詳細をキャッシュに保存する（既存があれば上書き）。"""
    payload = json.dumps(detail, ensure_ascii=False)
    now = datetime.now(timezone.utc)
    with SessionLocal() as session:
        row = session.query(CachedPlaceDetail).filter_by(place_id=place_id).one_or_none()
        if row is None:
            row = CachedPlaceDetail(place_id=place_id, payload_json=payload, fetched_at=now)
            session.add(row)
        else:
            row.payload_json = payload
            row.fetched_at = now
        session.commit()


def get_cached_photo(place_id: str) -> Optional[tuple[bytes, str]]:
    """有効なキャッシュがあれば店舗写真（バイナリ, content-type）を返す。無ければNone。"""
    with SessionLocal() as session:
        row = session.query(CachedPlacePhoto).filter_by(place_id=place_id).one_or_none()
        if row is None or not _is_fresh(row.fetched_at):
            return None
        return row.image_data, row.content_type


def save_photo_cache(place_id: str, image_data: bytes, content_type: str) -> None:
    """店舗写真をキャッシュに保存する（既存があれば上書き）。"""
    now = datetime.now(timezone.utc)
    with SessionLocal() as session:
        row = session.query(CachedPlacePhoto).filter_by(place_id=place_id).one_or_none()
        if row is None:
            row = CachedPlacePhoto(
                place_id=place_id, content_type=content_type, image_data=image_data, fetched_at=now
            )
            session.add(row)
        else:
            row.content_type = content_type
            row.image_data = image_data
            row.fetched_at = now
        session.commit()
