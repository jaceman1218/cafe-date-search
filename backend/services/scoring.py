"""検索結果のランキングロジック。

要件定義書 6章の評価要素（営業時間の一致・予算の一致・Google評価・口コミ数など）を
もとにスコアリングする。将来的に大幅な変更が想定されているため、
ロジックはこのモジュールに閉じ込め、他のコードから直接算出式を触らせない。
"""
from __future__ import annotations

import math
from typing import Any

from backend.schemas.search import BUDGET_PRICE_LEVEL_MAP, Budget, TimeSlot

# 各評価要素の重み（合計100点）。将来的にAI分析結果（初デートおすすめ度）を
# 組み込む際は、ここに新しい要素を追加していく想定。
WEIGHTS = {
    "opening_hours_match": 30,
    "budget_match": 20,
    "rating": 30,
    "review_count": 20,
}


def is_open_during_time_slot(opening_hours: dict[str, Any] | None, time_slot: TimeSlot) -> bool | None:
    """営業時間が指定の時間帯と重なっているかを判定する。

    Google Places の opening_hours.periods を厳密にパースするのはMVPの範囲を超えるため、
    ここでは periods の有無から簡易的に判定する。情報が取得できない場合は None（不明）を返す。

    TODO: periods を実際にパースして、時間帯との重なりを正確に判定する（MVP以降で精緻化）。
    """
    if not opening_hours or "periods" not in opening_hours:
        return None
    return True


def score_place(place: dict[str, Any], time_slot: TimeSlot, budget: Budget) -> float:
    """1店舗のスコア（0〜100点相当）を計算する。"""
    score = 0.0

    is_open = is_open_during_time_slot(place.get("opening_hours"), time_slot)
    if is_open:
        score += WEIGHTS["opening_hours_match"]
    elif is_open is None:
        score += WEIGHTS["opening_hours_match"] * 0.5  # 不明な場合は減点しすぎない

    price_level = place.get("price_level")
    low, high = BUDGET_PRICE_LEVEL_MAP[budget]
    if price_level is not None:
        if low <= price_level <= high:
            score += WEIGHTS["budget_match"]
    else:
        score += WEIGHTS["budget_match"] * 0.5

    rating = place.get("rating") or 0
    score += WEIGHTS["rating"] * (rating / 5)

    review_count = place.get("user_ratings_total") or 0
    # 口コミ数は対数的に評価し、極端な差がスコアを支配しすぎないようにする（1000件でほぼ満点）。
    normalized = min(math.log10(review_count + 1) / 3, 1.0)
    score += WEIGHTS["review_count"] * normalized

    return round(score, 1)


def rank_places(
    places: list[dict[str, Any]], time_slot: TimeSlot, budget: Budget
) -> list[tuple[dict[str, Any], float]]:
    """店舗リストをスコア降順に並び替える。"""
    scored = [(place, score_place(place, time_slot, budget)) for place in places]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored
