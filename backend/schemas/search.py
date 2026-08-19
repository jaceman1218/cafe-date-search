"""検索条件に関するスキーマ定義。"""
from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, Field, field_validator

MAX_AREAS = 5


class TimeSlot(str, Enum):
    """デートの時間帯。"""

    MORNING = "morning"  # 6:00-11:00
    DAY = "day"  # 11:00-17:00
    NIGHT = "night"  # 17:00-23:00


# 各時間帯の (開始時, 開始分, 終了時, 終了分)。営業時間との重なり判定に使う。
TIME_SLOT_RANGES = {
    TimeSlot.MORNING: (6, 0, 11, 0),
    TimeSlot.DAY: (11, 0, 17, 0),
    TimeSlot.NIGHT: (17, 0, 23, 0),
}


class Budget(str, Enum):
    """1人あたりの予算帯。"""

    UNDER_1000 = "under_1000"
    UNDER_2000 = "under_2000"
    UNDER_3000 = "under_3000"
    UNDER_5000 = "under_5000"
    OVER_5000 = "over_5000"


# Google Places の price_level (0〜4) との大まかな対応。
# 実際の金額情報が取得できるようになった段階で精緻化する。
BUDGET_PRICE_LEVEL_MAP = {
    Budget.UNDER_1000: (0, 1),
    Budget.UNDER_2000: (1, 2),
    Budget.UNDER_3000: (2, 2),
    Budget.UNDER_5000: (2, 3),
    Budget.OVER_5000: (3, 4),
}


class SearchRequest(BaseModel):
    """検索画面から送信される検索条件。"""

    areas: List[str] = Field(..., min_length=1, max_length=MAX_AREAS, description="駅・エリア名のリスト（最大5件）")
    time_slot: TimeSlot
    budget: Budget

    @field_validator("areas")
    @classmethod
    def _strip_and_validate(cls, value: List[str]) -> List[str]:
        cleaned = [v.strip() for v in value if v.strip()]
        if not cleaned:
            raise ValueError("駅・エリアを1件以上入力してください")
        if len(cleaned) > MAX_AREAS:
            raise ValueError(f"駅・エリアは最大{MAX_AREAS}件までです")
        return cleaned
