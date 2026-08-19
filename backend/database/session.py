"""SQLiteキャッシュDBの接続まわり。

Google Places APIの検索結果・店舗詳細をローカルのSQLiteファイルにキャッシュし、
同じエリア・同じ店舗への再アクセスでAPIを呼び直さずに済むようにする。

DBファイルの場所は環境変数 DATABASE_URL で変更できる
（例：本番でPostgreSQL等に差し替える場合 "postgresql://..."）。
未設定時はプロジェクトルート直下の cafe_search_cache.db を使う。
"""
from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "cafe_search_cache.db"
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{_DEFAULT_DB_PATH}")

# SQLiteは複数スレッドから同じコネクションを使うと警告が出るため check_same_thread=False にする。
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """キャッシュ用テーブルが無ければ作成する。main.py起動時に一度呼ぶ。"""
    from backend.models.cache import Base  # 循環importを避けるため関数内でimport

    Base.metadata.create_all(bind=engine)
