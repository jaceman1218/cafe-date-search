"""口コミAI分析の拡張ポイント（Phase 2で実装予定）。

MVPではAIを使用しないが、後から差し替えやすいようインターフェースだけ用意しておく。
呼び出し側（api/reviews.py）はこのモジュールの関数を呼ぶだけにし、
中身の実装がルールベース→AIに変わってもAPIの形は変えずに済むようにする。

将来的な分析予定項目（要件定義書 7章）：
- 会話しやすさ / 店内の騒がしさ / 店内の雰囲気 / 席の広さ
- 長居しやすさ / 混雑 / 店員対応
- 初デート利用に関する口コミ / マイナス評価 / 注意点
最終的に「初デートおすすめ度（0〜100）」として返す想定。
"""
from __future__ import annotations

from typing import Any, Optional, TypedDict


class ReviewAnalysisResult(TypedDict, total=False):
    """初デートおすすめ度などの分析結果（将来の型定義用プレースホルダ）。"""

    date_suitability_score: int  # 初デートおすすめ度 0〜100
    positive_points: list[str]
    caution_points: list[str]
    recommended_time_range: Optional[str]


async def analyze_reviews(reviews: list[dict[str, Any]]) -> Optional[ReviewAnalysisResult]:
    """口コミ一覧を分析し、初デート適性を判定する。

    MVPでは未実装。Phase 2でOpenAI API等を用いた実装に差し替える。
    呼び出し側は None が返ることを想定しておく（UI側は「分析準備中」等の表示にする）。
    """
    return None
