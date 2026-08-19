"""検索結果・店舗詳細のキャッシュ用DBモデル。

Google Places APIのレスポンスをそのままJSON文字列で保持する（スキーマの変更に
強くするため）。実際の中身の解釈は backend/services 側で行う。
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, LargeBinary, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CachedAreaSearch(Base):
    """エリア名ごとのカフェ検索結果（Google Places の生レスポンス）のキャッシュ。"""

    __tablename__ = "cached_area_searches"

    id: Mapped[int] = mapped_column(primary_key=True)
    area: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    payload_json: Mapped[str] = mapped_column(Text)  # results配列をJSON文字列化したもの
    fetched_at: Mapped[datetime] = mapped_column(DateTime)


class CachedPlaceDetail(Base):
    """place_idごとの店舗詳細（Google Places の生レスポンス）のキャッシュ。"""

    __tablename__ = "cached_place_details"

    id: Mapped[int] = mapped_column(primary_key=True)
    place_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    payload_json: Mapped[str] = mapped_column(Text)  # 店舗詳細1件分をJSON文字列化したもの
    fetched_at: Mapped[datetime] = mapped_column(DateTime)


class CachedPlacePhoto(Base):
    """place_idごとの代表写真（画像バイナリ本体）のキャッシュ。"""

    __tablename__ = "cached_place_photos"

    id: Mapped[int] = mapped_column(primary_key=True)
    place_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    content_type: Mapped[str] = mapped_column(String(100))
    image_data: Mapped[bytes] = mapped_column(LargeBinary)
    fetched_at: Mapped[datetime] = mapped_column(DateTime)
