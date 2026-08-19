"""口コミ関連のAPIエンドポイント（Phase 2 AI分析の受け皿）。"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.services.google_maps import GoogleMapsClient, GoogleMapsClientError
from backend.services.review_analyzer import analyze_reviews

router = APIRouter(prefix="/api/places", tags=["reviews"])


@router.get("/{place_id}/reviews")
async def get_place_reviews(place_id: str) -> dict:
    """店舗の口コミと、（将来の）AI分析結果を返す。

    MVPでは口コミの生データのみ意味を持ち、analysis は常に null。
    フロントエンドは analysis が null の間は「分析準備中」等の表示にしておく。
    """
    client = GoogleMapsClient()
    try:
        place = await client.get_place_details(place_id)
    except GoogleMapsClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    reviews = place.get("reviews", [])
    analysis = await analyze_reviews(reviews)

    return {
        "place_id": place_id,
        "reviews": reviews,
        "analysis": analysis,  # Phase 2で初デートおすすめ度などが入る予定
    }
