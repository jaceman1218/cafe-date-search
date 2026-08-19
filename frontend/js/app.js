// カフェデート検索 フロントエンドロジック（MVP：素のJSで実装）
//
// API_BASEの決め方：
// - window.APP_CONFIG.apiBase が設定されていれば最優先でそれを使う
// - frontend/index.html を file:// で直接開いた場合（ローカル開発）は
//   ローカルのバックエンド(localhost:8000)を指す
// - それ以外（http/https、Renderなどで配信された場合）は同一オリジンの
//   相対パスを使う（バックエンドがfrontendも配信する構成のため）
const API_BASE =
  window.APP_CONFIG?.apiBase ?? (window.location.protocol === "file:" ? "http://localhost:8000" : "");
const MAX_AREAS = 5;

const screens = {
  search: document.getElementById("screen-search"),
  results: document.getElementById("screen-results"),
  detail: document.getElementById("screen-detail"),
};

function showScreen(name) {
  Object.entries(screens).forEach(([key, el]) => {
    el.classList.toggle("is-hidden", key !== name);
  });
  window.scrollTo(0, 0);
}

document.querySelectorAll(".back-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const name = btn.dataset.target.replace("screen-", "");
    showScreen(name);
  });
});

// --- 検索画面：エリア追加（最大5件） ---
const areaInputsContainer = document.getElementById("area-inputs");
document.getElementById("add-area-btn").addEventListener("click", () => {
  const count = areaInputsContainer.querySelectorAll(".area-input").length;
  if (count >= MAX_AREAS) {
    alert(`駅・エリアは最大${MAX_AREAS}件まで追加できます`);
    return;
  }
  const input = document.createElement("input");
  input.type = "text";
  input.className = "area-input";
  input.placeholder = "例：大阪駅";
  areaInputsContainer.appendChild(input);
  input.focus();
});

// --- 検索画面：時間帯選択 ---
const timeSlotGroup = document.getElementById("time-slot-group");
let selectedTimeSlot = "day";
timeSlotGroup.addEventListener("click", (event) => {
  const btn = event.target.closest(".segmented-btn");
  if (!btn) return;
  timeSlotGroup.querySelectorAll(".segmented-btn").forEach((b) => b.classList.remove("is-selected"));
  btn.classList.add("is-selected");
  selectedTimeSlot = btn.dataset.value;
});

// --- 検索実行 ---
const TIME_SLOT_LABELS = { morning: "朝 6:00〜11:00", day: "昼 11:00〜17:00", night: "夜 17:00〜23:00" };
const BUDGET_LABELS = {
  under_1000: "〜1,000円",
  under_2000: "〜2,000円",
  under_3000: "〜3,000円",
  under_5000: "〜5,000円",
  over_5000: "5,000円〜",
};
const SORT_LABELS = {
  score: "おすすめ順",
  rating: "評価が高い順",
  reviews: "口コミが多い順",
  distance: "駅から近い順",
};

document.getElementById("search-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const areas = Array.from(areaInputsContainer.querySelectorAll(".area-input"))
    .map((input) => input.value.trim())
    .filter(Boolean);

  if (areas.length === 0) {
    alert("駅・エリアを1件以上入力してください");
    return;
  }

  const budget = document.querySelector('input[name="budget"]:checked').value;
  const sortBy = document.getElementById("search-sort-select").value;
  const limit = Number(document.getElementById("search-limit-select").value);
  const submitBtn = event.target.querySelector(".primary-btn");
  submitBtn.disabled = true;
  submitBtn.textContent = "検索中...";

  try {
    const response = await fetch(`${API_BASE}/api/places/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ areas, time_slot: selectedTimeSlot, budget, sort_by: sortBy, limit }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || "検索に失敗しました");
    }

    const data = await response.json();
    lastResults = data.results;
    document.getElementById("results-condition").textContent =
      `${data.searched_areas.join("・")} / ${TIME_SLOT_LABELS[selectedTimeSlot]} / ${BUDGET_LABELS[budget]} / ${SORT_LABELS[sortBy]} / ${limit}件`;
    // バックエンドが既に指定の並び順で返しているので、結果画面のプルダウンも合わせておく
    // （そこからさらに別の並び順に切り替えることも引き続き可能）
    document.getElementById("sort-select").value = sortBy;
    renderList(lastResults);
    showScreen("results");
  } catch (error) {
    alert(error.message);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "カフェを探す";
  }
});

let lastResults = [];

// 「駅から徒歩○分」等のテキストから分数を取り出す。「すぐ」は0分、
// 読み取れない場合は並び替え時に最後尾に回すよう非常に大きい値を返す。
function parseWalkMinutes(distanceText) {
  if (!distanceText) return Infinity;
  if (distanceText.includes("すぐ")) return 0;
  const match = distanceText.match(/(\d+)\s*分/);
  return match ? Number(match[1]) : Infinity;
}

function sortResults(results, sortKey) {
  const sorted = [...results];
  switch (sortKey) {
    case "rating":
      sorted.sort((a, b) => (b.rating ?? -1) - (a.rating ?? -1));
      break;
    case "reviews":
      sorted.sort((a, b) => (b.user_ratings_total ?? -1) - (a.user_ratings_total ?? -1));
      break;
    case "distance":
      sorted.sort((a, b) => parseWalkMinutes(a.distance_text) - parseWalkMinutes(b.distance_text));
      break;
    case "score":
    default:
      sorted.sort((a, b) => b.score - a.score);
      break;
  }
  return sorted;
}

document.getElementById("sort-select").addEventListener("change", (event) => {
  renderList(sortResults(lastResults, event.target.value));
});

function renderList(results) {
  const list = document.getElementById("results-list");
  list.innerHTML = "";

  if (results.length === 0) {
    list.innerHTML =
      '<p class="empty-state">条件に合うカフェが見つかりませんでした。エリアや条件を変えて試してください。</p>';
    return;
  }

  results.forEach((place, index) => {
    const card = document.createElement("div");
    card.className = "place-card";
    card.innerHTML = `
      <img class="place-photo" src="${API_BASE}/api/places/${place.place_id}/photo" alt=""
           loading="lazy" onerror="this.remove()">
      <h3>${index + 1}. ${escapeHtml(place.name)}</h3>
      <p class="meta">★ ${place.rating ?? "-"}　口コミ ${place.user_ratings_total ?? "-"}件</p>
      <p class="meta">${escapeHtml(place.address ?? "")}</p>
      ${place.distance_text ? `<p class="meta">${escapeHtml(place.distance_text)}</p>` : ""}
    `;
    card.addEventListener("click", () => openDetail(place.place_id));
    list.appendChild(card);
  });
}

// --- 店舗詳細 ---
async function openDetail(placeId) {
  const content = document.getElementById("detail-content");
  content.innerHTML = "<p>読み込み中...</p>";
  showScreen("detail");

  try {
    const response = await fetch(`${API_BASE}/api/places/${placeId}`);
    if (!response.ok) throw new Error("店舗情報の取得に失敗しました");
    const place = await response.json();

    content.innerHTML = `
      <div class="detail-block">
        <img class="detail-photo" src="${API_BASE}/api/places/${place.place_id}/photo" alt=""
             loading="lazy" onerror="this.remove()">
        <h2>${escapeHtml(place.name)}</h2>
        <dl>
          <dt>評価</dt><dd>★ ${place.rating ?? "-"}（口コミ ${place.user_ratings_total ?? "-"}件）</dd>
          <dt>住所</dt><dd>${escapeHtml(place.address ?? "-")}</dd>
          <dt>アクセス</dt><dd>${escapeHtml(place.distance_text ?? "-")}</dd>
          <dt>営業時間</dt><dd>${(place.opening_hours_text ?? "-").replace(/\n/g, "<br>")}</dd>
          <dt>電話番号</dt><dd>${escapeHtml(place.formatted_phone_number ?? "-")}</dd>
        </dl>
        <a class="maps-link-btn" href="${place.google_maps_url}" target="_blank" rel="noopener">Googleマップで見る</a>
      </div>
    `;
  } catch (error) {
    content.innerHTML = `<p class="error-state">${escapeHtml(error.message)}</p>`;
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}
