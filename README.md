# 旅行計画エージェント (travel-planner-agent)

## 概要
【渋谷】Zenn Agentic AI ミニハッカソン with Google Cloud (2026/09/05)  
イベントページ: https://events.classmethod.jp/study-club/connpass-398578/

本リポジトリは、上記のイベント内デモ（13:00-13:45）にて、`agents-cli` を活用してゼロから作成・テスト・デプロイした旅行計画エージェントのソースコードおよび再現手順書です。

## 主な特徴とアーキテクチャ
- **モデル**: `gemini-3.8-flash`
- **フレームワーク**: Google ADK (Agent Development Kit, `google-adk==2.8.0`)
- **外部連携ツール**:
  - **Google Maps MCP Server**: リモートエンドポイント (Streamable HTTP / SSE) 経由でスポット検索・ルート・所要時間算出を実施
  - **Google Search**: ADK ネイティブツールを用いて最新の観光地情報・イベント・営業時間をリサーチ
- **デプロイ先**: Gemini Enterprise Agent Platform (Agent Runtime)
- **開発手法**: テスト駆動開発 (TDD / pytest) によるインターフェース検証 + `agents-cli eval` による旅行プラン品質評価

## リポジトリ構成
- `app/`: エージェント本体コード
  - `app/agent.py`: Google Maps MCP と Google Search を統合したエージェント定義
  - `app/fast_api_app.py`: FastAPI バックエンドサーバー
- `tests/`: テストスイート
  - `tests/unit/`: pytest によるユニットテスト
  - `tests/integration/`: MCP 統合テスト
  - `tests/eval/`: 評価データセットと評価設定
- `demo_procedure.md`: デモ中に実施した各ターン（Turn 1〜6）の投入プロンプトと詳細手順書
- `.agents-cli-spec.md`: エージェントの初期仕様定義書
- `pyproject.toml` / `uv.lock`: 依存関係定義
- `Dockerfile`: コンテナビルド定義

## クイックスタート (ローカル実行)

### 1. 前提条件
- Python 3.12 (`python3.12`)
- uv パッケージマネージャー
- Google Cloud CLI (`gcloud`)
- agents-cli (`uv tool install google-agents-cli`)

### 2. 環境変数の設定
`.env.example` をコピーして `.env` を作成し、必要な設定を行ってください。

```bash
cp .env.example .env
```

`.env` の主要設定項目:
- `GOOGLE_GENAI_USE_VERTEXAI=true`
- `GOOGLE_CLOUD_PROJECT=<YOUR_PROJECT_ID>`
- `GOOGLE_CLOUD_LOCATION=us-central1`
- `MAPS_API_KEY=<YOUR_GOOGLE_MAPS_API_KEY>`
- `GOOGLE_MAPS_MCP_SERVER_URL=https://mapstools.googleapis.com/mcp`

### 3. テストの実行 (pytest)
```bash
uv run pytest
```

### 4. ローカルでの対話・動作確認

**CLI による実行:**
```bash
agents-cli run "京都の1泊2日の旅行プランを提案してください。金閣寺と嵐山に行きたいです。"
```

**Playground (Web UI) による対話実行:**
```bash
agents-cli playground
```
実行後、ブラウザで `http://127.0.0.1:8080/dev-ui/?app=app` を開くことで、チャット形式で旅行プランの生成やツール（Google Maps MCP / Google Search）の呼び出し状況を視覚的に確認できます。

## デモ手順の再現
デモ全体の流れ（プロジェクト初期化、TDDによるテスト・本体実装、評価、デプロイ）の投入プロンプトや詳細な解説については、[demo_procedure.md](demo_procedure.md) をご参照ください。