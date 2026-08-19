"""APIキー未設定時に使うダミーの店舗データ（動作確認用）。

本番のGoogle Places APIレスポンスと同じ形（place_id, name, rating, ...）に
揃えてあるので、services/scoring.py や api/places.py はモックか実データかを
意識せずに動く。GOOGLE_MAPS_API_KEY を設定すれば自動的に使われなくなる。

店名・住所・営業時間は梅田エリアの実在カフェを参考にしたものだが、
rating（評価）・user_ratings_total（口コミ数）・reviews（口コミ本文）・
formatted_phone_number（電話番号）・website は Google Places API から
取得したものではなく、UI確認用の仮の値であることに注意する。
"""
from __future__ import annotations

from typing import Any


def _hours(start: str, end: str) -> dict[str, Any]:
    """簡易的な営業時間データを作る（全曜日同じ時間として扱う）。"""
    return {
        "periods": [{"open": {"time": start}, "close": {"time": end}}],
        "weekday_text": [f"月〜日: {start[:2]}:{start[2:]}〜{end[:2]}:{end[2:]}"],
    }


MOCK_PLACES: list[dict[str, Any]] = [
    {
        "place_id": "mock-place-1",
        "name": "ブルーバード",
        "rating": 4.3,
        "user_ratings_total": 850,
        "price_level": 2,
        "formatted_address": "大阪市北区角田町8-1 梅田阪急ビル 15F",
        "distance_text": "阪急梅田駅から徒歩3分",
        "opening_hours": _hours("1100", "2330"),
        "formatted_phone_number": None,
        "website": None,
        "url": "https://maps.google.com/?q=ブルーバード+梅田阪急ビル",
        "reviews": [
            {"text": "（サンプル口コミ）夜景が見える高層階の落ち着いた雰囲気で会話がはずみました。"},
            {"text": "（サンプル口コミ）席がゆったりしていて長居しやすい。"},
        ],
    },
    {
        "place_id": "mock-place-2",
        "name": "chano-ma 茶屋町",
        "rating": 4.2,
        "user_ratings_total": 620,
        "price_level": 2,
        "formatted_address": "大阪市北区茶屋町10-12 NU茶屋町 9F",
        "distance_text": "阪急梅田駅から徒歩3分",
        "opening_hours": _hours("1100", "2200"),
        "formatted_phone_number": None,
        "website": None,
        "url": "https://maps.google.com/?q=chano-ma+茶屋町",
        "reviews": [
            {"text": "（サンプル口コミ）ソファ席でくつろげる。初デートにも使いやすい。"},
        ],
    },
    {
        "place_id": "mock-place-3",
        "name": "Wired café NU茶屋町",
        "rating": 4.0,
        "user_ratings_total": 1500,
        "price_level": 1,
        "formatted_address": "大阪市北区茶屋町10-12 NU chayamachi 2F",
        "distance_text": "阪急梅田駅から徒歩5分",
        "opening_hours": _hours("1100", "2300"),
        "formatted_phone_number": None,
        "website": None,
        "url": "https://maps.google.com/?q=Wired+café+NU茶屋町",
        "reviews": [
            {"text": "（サンプル口コミ）カジュアルで入りやすく、初対面でも緊張しにくい。"},
        ],
    },
    {
        "place_id": "mock-place-4",
        "name": "MAISON ICHI PLUS（メゾン・イチ プリュス）",
        "rating": 4.4,
        "user_ratings_total": 430,
        "price_level": 2,
        "formatted_address": "大阪市北区茶屋町8-26 NU茶屋町プラス 3F",
        "distance_text": "阪急梅田駅からすぐ",
        "opening_hours": _hours("1100", "2130"),
        "formatted_phone_number": None,
        "website": None,
        "url": "https://maps.google.com/?q=MAISON+ICHI+PLUS+茶屋町",
        "reviews": [
            {"text": "（サンプル口コミ）内装がおしゃれで写真映えする。"},
        ],
    },
    {
        "place_id": "mock-place-5",
        "name": "café & books bibliotheque",
        "rating": 4.1,
        "user_ratings_total": 380,
        "price_level": 1,
        "formatted_address": "大阪市北区梅田1-12-6 E-ma B1F",
        "distance_text": "西梅田駅から徒歩すぐ",
        "opening_hours": _hours("1100", "2100"),
        "formatted_phone_number": None,
        "website": None,
        "url": "https://maps.google.com/?q=café+books+bibliotheque+梅田",
        "reviews": [
            {"text": "（サンプル口コミ）本に囲まれた空間で静かに話せる。"},
        ],
    },
    {
        "place_id": "mock-place-6",
        "name": "The 33 Tea＆Bar Terrace",
        "rating": 4.5,
        "user_ratings_total": 290,
        "price_level": 3,
        "formatted_address": "大阪市北区梅田2-4-9 ブリーゼブリーゼ33階",
        "distance_text": "西梅田駅から徒歩3分",
        "opening_hours": {
            "periods": [
                {"open": {"time": "1100"}, "close": {"time": "1600"}},
                {"open": {"time": "1700"}, "close": {"time": "2200"}},
            ],
            "weekday_text": ["月〜日: 11:00〜16:00 / 17:00〜22:00"],
        },
        "formatted_phone_number": None,
        "website": None,
        "url": "https://maps.google.com/?q=The+33+Tea+Bar+Terrace+梅田",
        "reviews": [
            {"text": "（サンプル口コミ）高層階からの眺めが良く特別感がある。夜デート向き。"},
        ],
    },
    {
        "place_id": "mock-place-7",
        "name": "SOHOLM CAFE+DINING",
        "rating": 4.0,
        "user_ratings_total": 510,
        "price_level": 2,
        "formatted_address": "大阪市北区大深町3-1 グランフロント大阪 北館1F",
        "distance_text": "JR大阪駅から徒歩3分",
        "opening_hours": _hours("1100", "2100"),
        "formatted_phone_number": None,
        "website": None,
        "url": "https://maps.google.com/?q=SOHOLM+CAFE+DINING+グランフロント大阪",
        "reviews": [
            {"text": "（サンプル口コミ）駅から近くアクセスが良い。"},
        ],
    },
    {
        "place_id": "mock-place-8",
        "name": "24/7café apartment 梅田店",
        "rating": 3.9,
        "user_ratings_total": 980,
        "price_level": 1,
        "formatted_address": "大阪市北区大深町4-1 グランフロント大阪 うめきた広場B1F",
        "distance_text": "JR大阪駅からすぐ",
        "opening_hours": _hours("1000", "2200"),
        "formatted_phone_number": None,
        "website": None,
        "url": "https://maps.google.com/?q=24/7café+apartment+梅田店",
        "reviews": [
            {"text": "（サンプル口コミ）カジュアルで自然な雰囲気、初デートの緊張がほぐれる。"},
        ],
    },
    {
        "place_id": "mock-place-9",
        "name": "ティーラウンジ パルテール",
        "rating": 4.3,
        "user_ratings_total": 150,
        "price_level": 3,
        "formatted_address": "大阪市北区茶屋町19-19 ホテル阪急インターナショナル 2F",
        "distance_text": "阪急梅田駅 茶屋町口から徒歩3分",
        "opening_hours": _hours("0900", "1930"),
        "formatted_phone_number": None,
        "website": None,
        "url": "https://maps.google.com/?q=ティーラウンジ+パルテール",
        "reviews": [
            {"text": "（サンプル口コミ）ホテルラウンジならではの上品な雰囲気で朝・昼デートにおすすめ。"},
        ],
    },
    {
        "place_id": "mock-place-10",
        "name": "NITO Coffee&Craft Beer",
        "rating": 4.2,
        "user_ratings_total": 210,
        "price_level": 2,
        "formatted_address": "大阪市北区堂島2-2-22 1F",
        "distance_text": "西梅田駅から徒歩約6分",
        "opening_hours": _hours("1100", "2300"),
        "formatted_phone_number": None,
        "website": None,
        "url": "https://maps.google.com/?q=NITO+Coffee+Craft+Beer+堂島",
        "reviews": [
            {"text": "（サンプル口コミ）コーヒーもクラフトビールも楽しめて、昼から夜まで使いやすい。"},
        ],
    },
]


def get_mock_cafes(area: str) -> list[dict[str, Any]]:
    """検索エリアに応じたダミーのカフェ一覧を返す（実データと同じ形）。

    MVPのモックでは area による絞り込みはせず、常に同じ10件を返す。
    """
    return MOCK_PLACES


def get_mock_place_detail(place_id: str) -> dict[str, Any]:
    """place_idに対応するダミー詳細を返す。見つからなければ空dict。"""
    for place in MOCK_PLACES:
        if place["place_id"] == place_id:
            return place
    return {}
