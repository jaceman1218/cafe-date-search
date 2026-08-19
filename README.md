# カフェデート検索（MVP）

デート経験が少ない人向けに、「駅・エリア」「時間帯」「予算」の3つだけを入力すれば、
初デートに使いやすいカフェを提示するWebアプリ。

詳しい背景・仕様は [docs/requirements.md](docs/requirements.md) を参照。

## 構成

```text
.
├── backend/          FastAPI バックエンド
│   ├── main.py       エントリーポイント
│   ├── api/          エンドポイント（places / reviews）
│   ├── services/      Google Maps連携・スコアリング・AI分析（将来用）
│   ├── schemas/       Pydanticスキーマ
│   ├── models/        DBモデル（検索結果・店舗詳細のキャッシュ）
│   └── database/      DB接続（SQLite）
├── frontend/          素のHTML/CSS/JS
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
├── tests/             pytest
├── docs/requirements.md  要件定義書
├── requirements.txt
├── .env.example
└── .gitignore
```

## セットアップ（ローカル開発）

### 1. Google Maps Platform APIキーを取得

Google Cloud Console で **Places API** を有効化し、APIキーを発行する。

> **APIキーがまだ無い場合**：`GOOGLE_MAPS_API_KEY` を設定しないままサーバーを起動すると、
> 自動的に「モックモード」で動作し、実際のGoogle APIを呼ばずにダミーのカフェ3件
> （`backend/services/mock_data.py`）を返す。検索〜詳細画面までの動作確認はこれで可能。
> `.env`にキーを設定すれば自動的に実データに切り替わる。

### 2. 環境変数の設定

```bash
cp .env.example .env
# .env を開いて GOOGLE_MAPS_API_KEY を設定する
```

`.env` はGitに含めない（`.gitignore` 済み）。

### 3. バックエンドの起動

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

`http://localhost:8000/api/health` にアクセスして `{"status":"ok"}` が返れば起動成功。

### 4. フロントエンドの起動

`frontend/index.html` を直接ブラウザで開くか、簡易サーバーで配信する。

```bash
cd frontend
python -m http.server 5500
```

`http://localhost:5500` を開く。バックエンドのURLは `frontend/js/app.js` の
`API_BASE`（デフォルト `http://localhost:8000`）で変更できる。

### 5. テストの実行

```bash
pytest
```

## 検索結果のキャッシュ

Google Places APIの呼び出し回数を減らすため、検索結果（エリア単位）と店舗詳細を
SQLite（プロジェクトルート直下 `cafe_search_cache.db`、`.gitignore`済み）にキャッシュする。

- 同じエリアを再検索しても、キャッシュが新しければ（デフォルトTTL: 24時間）Google APIを呼ばずにDBから返す
- TTLは環境変数 `CACHE_TTL_HOURS` で変更可能
- キャッシュDBの接続先は環境変数 `DATABASE_URL` で変更可能（デフォルトはSQLiteファイル）
- モックモード時はキャッシュを使わない（ダミーデータは常にメモリ上の固定値のため）

キャッシュを作り直したい場合は `cafe_search_cache.db` を削除すればよい（次回起動時に自動再作成される）。

## API概要

| メソッド | パス | 内容 |
| --- | --- | --- |
| POST | `/api/places/search` | 駅・エリア（複数可）＋時間帯＋予算でカフェを検索 |
| GET | `/api/places/{place_id}` | 店舗詳細を取得 |
| GET | `/api/places/{place_id}/photo` | 店舗の代表写真（画像バイナリ）を返す。APIキーはバックエンド内に留め、フロントには渡さない。写真が無い店舗・モックモードでは404 |
| GET | `/api/places/{place_id}/reviews` | 口コミ取得（`analysis`はPhase 2まで常に`null`） |
| GET | `/api/health` | ヘルスチェック |

## 今後の拡張ポイント

- `backend/services/review_analyzer.py` … Phase 2の口コミAI分析をここに実装する（`analyze_reviews()`を実装するだけでAPIの形は変えずに済む構造）。
- `backend/services/scoring.py` … ランキングロジック。AI分析結果をスコアに組み込む際もここを変更する。
- `backend/models/` / `backend/database/` … 現状は検索結果・店舗詳細のキャッシュのみ。口コミ分析結果の永続化などが必要になったらここに追加する。

## デプロイ（Render）

FastAPIが `frontend/` の静的ファイルも配信するため、**バックエンド1サービスだけ**で
アプリ全体（画面＋API）が動く構成になっている。フロントエンドを別サービスに分ける必要はない。

### 手順

1. GitHubにこのリポジトリをpush
2. Renderのダッシュボードで「New +」→「Blueprint」→ このリポジトリを選択
   （リポジトリ直下の `render.yaml` の内容が自動で読み込まれる）
3. デプロイ時に `GOOGLE_MAPS_API_KEY` の入力を求められるので、Google Cloud Consoleで
   発行したキーを入力（`.env`と同様、リポジトリには含めない）
4. デプロイ完了後に払い出されるURL（例: `https://cafe-date-search.onrender.com`）に
   アクセスすればアプリが使える

`render.yaml` を使わず手動でWeb Serviceを作る場合は、以下を設定する。

| 項目 | 値 |
| --- | --- |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |
| Environment Variables | `GOOGLE_MAPS_API_KEY`（必須）、`CACHE_TTL_HOURS`（任意、デフォルト24） |

### 注意：SQLiteキャッシュの永続性

Renderの無料プランはファイルシステムが**再デプロイ・再起動のたびにリセット**される
（永続ディスクは有料プランのアドオン）。そのため `cafe_search_cache.db` によるキャッシュも
デプロイのたびに消える。動作には支障ないが、キャッシュの効果は再起動までの間に限られる。
永続化したい場合は、Renderの有料永続ディスク、または外部DB（`DATABASE_URL`で切り替え可能）
の利用を検討する。

### 将来AIを導入したら

`OPENAI_API_KEY` をRenderのEnvironment Variablesに追加する（`render.yaml`にも
`sync: false`で項目を追加しておくと、Blueprint適用時に入力を求められるようになる）。
