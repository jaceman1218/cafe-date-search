"""place_cache.py（検索結果・店舗詳細のSQLiteキャッシュ）のテスト。"""
from backend.database.session import init_db
from backend.services.place_cache import (
    get_cached_place_detail,
    get_cached_places,
    save_place_detail_cache,
    save_places_cache,
)

init_db()

TEST_AREA = "__pytest_cache_test_area__"
TEST_PLACE_ID = "__pytest_cache_test_place__"


def test_area_cache_roundtrip():
    assert get_cached_places(TEST_AREA) is None

    places = [{"place_id": "p1", "name": "テストカフェ"}]
    save_places_cache(TEST_AREA, places)

    cached = get_cached_places(TEST_AREA)
    assert cached == places


def test_place_detail_cache_roundtrip():
    assert get_cached_place_detail(TEST_PLACE_ID) is None

    detail = {"place_id": TEST_PLACE_ID, "name": "テスト詳細カフェ"}
    save_place_detail_cache(TEST_PLACE_ID, detail)

    cached = get_cached_place_detail(TEST_PLACE_ID)
    assert cached == detail
