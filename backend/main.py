"""カフェデート検索 バックエンドのエントリーポイント。

ローカル起動（推奨・reload対応）:
    uvicorn backend.main:app --reload

このファイルを直接実行（IDEの▶ボタン等）しても起動できる。
"""
from __future__ import annotations

import sys
from pathlib import Path

if __name__ == "__main__":
    # 直接実行された場合、`backend`パッケージをimportできるようプロジェクトルートを
    # sys.pathに追加しておく（`uvicorn backend.main:app`で起動する場合は不要）。
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()  # backend.api 配下が GOOGLE_MAPS_API_KEY を参照する前に読み込む

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

from backend.api import places, reviews  # noqa: E402
from backend.database.session import init_db  # noqa: E402

init_db()  # キャッシュ用テーブルが無ければ作成する

app = FastAPI(title="カフェデート検索 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # MVPでは簡易設定。本番では許可するオリジンを絞る。
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(places.router)
app.include_router(reviews.router)


@app.get("/api/health")
async def health_check() -> dict:
    return {"status": "ok"}


# フロントエンド（frontend/）を同じサービスから配信する。
# Renderへのデプロイをbackend/frontendの2サービスに分けずに済むよう、
# FastAPI自体が静的ファイルサーバーも兼ねる構成にしている。
# ローカルでは frontend/index.html を直接開いても動く（js/app.js側で自動切り替え）。
# 必ず他のルート（/api/*, /docs等）より後にmountすること。
_frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if _frontend_dir.is_dir():
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    # reload=Trueにしたい場合は `uvicorn backend.main:app --reload` を使うこと
    # （直接実行だとreload用の再importがプロジェクトルート基準にならず失敗するため）。
    uvicorn.run(app, host="127.0.0.1", port=8000)
