"""カフェ検索・店舗詳細のAPIエンドポイント。"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response

from backend.schemas.place import PlaceDetail, PlaceSummary, SearchResponse
from backend.schemas.search import SearchRequest
from backend.services.google_maps import GoogleMapsClient, GoogleMapsClientError
from backend.services.place_cache import get_cached_photo, save_photo_cache
from backend.services.scoring import rank_places

router = APIRouter(prefix="/api/places", tags=["places"])


def _to_summary(place: dict, area: str, score: float) -> PlaceSummary:
    place_id = place["place_id"]
    return PlaceSummary(
        place_id=place_id,
        name=place.get("name", ""),
        rating=place.get("rating"),
        user_ratings_total=place.get("user_ratings_total"),
        price_level=place.get("price_level"),
        address=place.get("formatted_address"),
        area=area,
        distance_text=place.get("distance_text"),
        opening_hours_text=None,
        is_open_in_time_slot=None,
        google_maps_url=f"https://www.google.com/maps/place/?q=place_id:{place_id}",
        score=score,
    )


@router.post("/search", response_model=SearchResponse)
async def search_places(request: SearchRequest) -> SearchResponse:
    """複数エリアのカフェをまとめて検索し、スコア順に返す。"""
    client = GoogleMapsClient()
    all_results: list[PlaceSummary] = []
    seen_place_ids: set[str] = set()

    for area in request.areas:
        try:
            places = await client.search_cafes(area)
        except GoogleMapsClientError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        ranked = rank_places(places, request.time_slot, request.budget)
        for place, score in ranked:
            place_id = place.get("place_id")
            if not place_id or place_id in seen_place_ids:
                continue  # 複数エリアの検索結果が重複した店舗は最初に見つかった方を採用
            seen_place_ids.add(place_id)
            all_results.append(_to_summary(place, area, score))

    all_results.sort(key=lambda p: p.score, reverse=True)
    return SearchResponse(results=all_results, searched_areas=request.areas)


@router.get("/{place_id}", response_model=PlaceDetail)
async def get_place_detail(place_id: str) -> PlaceDetail:
    """店舗詳細を取得する。"""
    client = GoogleMapsClient()
    try:
        place = await client.get_place_details(place_id)
    except GoogleMapsClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if not place:
        raise HTTPException(status_code=404, detail="店舗が見つかりませんでした")

    reviews = place.get("reviews", [])
    opening_hours = place.get("opening_hours", {})
    return PlaceDetail(
        place_id=place_id,
        name=place.get("name", ""),
        rating=place.get("rating"),
        user_ratings_total=place.get("user_ratings_total"),
        price_level=place.get("price_level"),
        address=place.get("formatted_address"),
        area="",
        distance_text=place.get("distance_text"),
        opening_hours_text="\n".join(opening_hours.get("weekday_text", [])) or None,
        is_open_in_time_slot=None,
        google_maps_url=place.get("url", f"https://www.google.com/maps/place/?q=place_id:{place_id}"),
        formatted_phone_number=place.get("formatted_phone_number"),
        website=place.get("website"),
        reviews_preview=[r.get("text", "") for r in reviews[:5]],
    )


@router.get("/{place_id}/photo")
async def get_place_photo(place_id: str) -> Response:
    """店舗の代表写真（1枚目）を返す。

    Google Places Photo APIへのバックエンド経由のプロキシ。APIキーをフロントエンドに
    渡さずに済むよう、ここで画像バイナリを取得してそのまま返す。写真が無い店舗や
    モックモードでは404を返すので、フロントエンドはimgのonerrorで「写真なし」を表現する。
    """
    cached = get_cached_photo(place_id)
    if cached is not None:
        content, content_type = cached
        return Response(content=content, media_type=content_type)

    client = GoogleMapsClient()
    try:
        place = await client.get_place_details(place_id)
    except GoogleMapsClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    photos = place.get("photos") or []
    photo_reference = photos[0].get("photo_reference") if photos else None
    if not photo_reference:
        raise HTTPException(status_code=404, detail="この店舗の写真は見つかりませんでした")

    try:
        content, content_type = await client.get_photo_bytes(photo_reference)
    except GoogleMapsClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    save_photo_cache(place_id, content, content_type)
    return Response(content=content, media_type=content_type)
