# agents-cli と Google Maps MCP / Google Search を用いた旅行計画エージェント開発・デプロイ手順

本ドキュメントは、`agents-cli` を使用してリモートエンドポイントの **Google Maps MCP (Model Context Protocol) サーバー** および **Google Search** と連携する ADK (Agent Development Kit) 旅行計画エージェントを開発し、**Agent Runtime** (Vertex AI Agent Engine) にデプロイするデモの実行手順およびプロンプト集である。

---

## 1. システム構成と前提条件

- **プロジェクト名**: `travel-planner-agent`
- **モデル**: `gemini-3.8-flash`
- **デプロイ先**: Agent Runtime (`--deployment-target agent_runtime`)
- **連携ツール**:
  - **Google Maps MCP Server**: リモートエンドポイント (Streamable HTTP / SSE)。スポット検索、地点間のルート・所要時間算出を担当。
  - **Google Search**: ADK ネイティブツール。最新の観光情報、イベント、見どころ、営業時間等のリサーチを担当。
- **実行環境**: Python 3.12 (`python3.12`), `uv` (パッケージマネージャー)
- **パッケージインデックス**: `https://pypi.org/simple`
- **開発手法**: テスト駆動開発 (TDD / pytest)

事前確認コマンド:

```bash
# uv の確認
uv --version

# agents-cli のインストールおよび確認
uv tool install google-agents-cli
agents-cli info
```

---

## 2. 全体ワークフロー

| ターン | フェーズ | 内容 |
|---|---|---|
| Turn 1 | Phase 0 & 2 | 旅行計画エージェントの仕様定義 (`.agents-cli-spec.md`) とプロジェクト初期化 |
| Turn 2 | 環境設定 | 依存関係 (`google-adk[mcp]`) 追加と MCP/API 接続設定 |
| Turn 3 | Phase 3 (TDD) | テストコード (pytest) の先行作成 |
| Turn 4 | Phase 3 (実装) | Google Maps MCP + Google Search 統合エージェントの実装とスモークテスト |
| Turn 5 | Phase 4 (評価) | `agents-cli eval` による旅行プランの妥当性・ツール呼び出し検証 |
| Turn 6 | Phase 5 (デプロイ) | Agent Runtime へのデプロイと疎通確認 |

---

## 3. 各ターンごとのプロンプトと実行手順

### Turn 1: 仕様定義とプロジェクトの初期化 (Phase 0 & 2)

#### 投入プロンプト

```text
agents-cli を使って、Google Maps MCP Server および Google Search と連携する ADK 旅行計画エージェントの新規プロジェクトを作成してください。

【要件】
1. デプロイ先ターゲット: agent_runtime (Vertex AI Agent Engine)
2. 使用モデル: gemini-3.8-flash
3. Python バージョン: 3.12
4. プロジェクト名: travel-planner-agent
5. 概要: 
   - ユーザーの希望（目的地、日数、予算、同行者など）に応じた旅行日程プランを作成する。
   - リモートの Google Maps MCP サーバーを呼び出し、スポットの正確な位置・移動ルート・所要時間を算出する。
   - Google Search を利用して、現地の最新イベントや見どころ、おすすめ情報を検索・反映する。

まずは Phase 0 として仕様を整理し、`.agents-cli-spec.md` を作成した上で、`agents-cli scaffold create travel-planner-agent --deployment-target agent_runtime` を実行してプロジェクト構造を生成してください。
```

#### 解説とチェックポイント
- `agents-cli scaffold create` により、エージェント定義、テスト、デプロイ用インフラ定義が一式生成される。
- `.agents-cli-spec.md` にモデル名 `gemini-3.8-flash`、ターゲット `agent_runtime`、2つのツール（Google Maps MCP、Google Search）が正しく記載されているか確認する。

---

### Turn 2: 依存パッケージの追加と環境設定

#### 投入プロンプト

```text
生成したプロジェクトに、リモート MCP クライアントおよび検索ツールに必要なパッケージと環境変数を設定してください。

【指示】
1. パッケージ管理には uv を使用し、インデックスに https://pypi.org/simple を指定して MCP 拡張版の ADK を追加してください:
   uv add "google-adk[mcp]" --index https://pypi.org/simple
2. Google Maps MCP サーバーのエンドポイント URL および API キー設定を `.env` または設定ファイルに追加してください:
   - MAPS_API_KEY="YOUR_GOOGLE_MAPS_API_KEY"
   - GOOGLE_MAPS_MCP_SERVER_URL="https://mapstools.googleapis.com/mcp"
   - GOOGLE_GENAI_USE_VERTEXAI="true"
   - GOOGLE_CLOUD_LOCATION="us-central1"
3. 秘密情報やクレデンシャルが直接コミットされないよう、`.env` が `.gitignore` に含まれていることを確認し、テンプレートとして `.env_example` を作成してください。
```

#### 解説とチェックポイント
- `google-adk[mcp]` の追加により、`StreamableHTTPConnectionParams` および `McpToolset` が利用可能になる。
- リモート MCP サーバーのエンドポイント URL を環境変数から動的に読み込めるように構成する。

---

### Turn 3: TDDによるテストコードの先行作成 (Phase 3 - テストファースト)

#### 投入プロンプト

```text
エージェントの実装に入る前に、TDD（テスト駆動開発）に従って pytest によるユニットテストと統合テストコードを作成してください。

【テスト要件】
1. テストファイル: `tests/test_agent.py`
2. テスト内容:
   - エージェントのインスタンス生成確認 (モデルが gemini-3.8-flash に設定されていること)
   - ツール構成の検証 (McpToolset と Google Search ツールが両方登録されていること)
   - リモート Maps MCP ツールの接続パラメータ設定検証
   - スポット検索・ルート案内のモックテスト (MCP から位置・所要時間データが返された際の処理ハンドリング)
3. 制約事項:
   - python3.12 コマンド、または `uv run pytest` で実行可能な構成にすること。
   - LLM 生成文の文言比較ではなく、インターフェース契約や関数呼び出し構造をアサートすること。
   - コード内の日本語コメントは体言止めまたは普通体で記述し、絵文字は使用しないこと。

テスト作成後、`uv run pytest` を実行し、本体未実装のため失敗（Red状態）することを確認してください。
```

#### 解説とチェックポイント
- 実装前にテストを作成し、意図通りテストが失敗することを確認する（Red）。
- テスト内でモックを活用し、リモートサーバーが停止していてもローカルテストが独立して実行できるようにする。

---

### Turn 4: エージェント本体の実装とローカルスモークテスト (Phase 3 - 実装)

#### 投入プロンプト

```text
Turn 3 で作成したテストを通過（Green）させるよう、エージェント本体の実装を行ってください。

【実装要件】
1. 実装ファイル: `travel_planner_agent/agent.py`
2. 内容:
   - `google.adk.tools.mcp_tool.McpToolset` および `StreamableHTTPConnectionParams` を使用してリモートの Google Maps MCP サーバーへ接続。
   - ADK の `google_search` ツールを追加。
   - root_agent (LlmAgent) にモデル `gemini-3.8-flash`、両ツールセット、および旅行日程作成用システムプロンプトを設定。
   - プロンプト指示:
     - 観光スポットやルート案内には Google Maps MCP ツールを利用し、正確な移動時間・ルートを算出する。
     - スポットの最新情報、イベント、営業時間、評判等の調査には Google Search を利用する。
     - 移動時間に無理のないタイムスケジュール表（1日目、2日目など）を構成して出力する。
3. 検証:
   - `uv run pytest` を実行してテストが全て通過することを確認。
   - `agents-cli run "京都の1泊2日の旅行プランを提案してください。金閣寺と嵐山に行きたいです。"` を実行して、ローカル環境でのスモークテストを実施してください。
4. 制約事項:
   - コード内の日本語コメントは体言止めまたは普通体で記述すること。
   - コード内およびログに絵文字を使用しないこと。
```

#### 実装参考コード (概要)

```python
import os
from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

# Google Maps MCP サーバーのエンドポイントおよび API キー取得
mcp_server_url = os.environ.get(
    "GOOGLE_MAPS_MCP_SERVER_URL",
    "https://mapstools.googleapis.com/mcp"
)
maps_api_key = os.environ.get("MAPS_API_KEY", "")

# Maps MCP ツールセット定義
maps_mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=mcp_server_url,
        headers={"X-Goog-Api-Key": maps_api_key}
    )
)

# ルートエージェント定義
root_agent = LlmAgent(
    name="travel_planner_agent",
    model="gemini-3.8-flash",
    instruction=(
        "あなたはプロの旅行プランナーです。"
        "ユーザーの要望に基づいて実行可能で無理のない旅行プランを作成します。\n"
        "1. 目的地の位置情報、ルート、移動時間の算出には Google Maps MCP ツールを使用すること。\n"
        "2. 最新の観光地情報、おすすめスポット、営業時間、イベントの確認には Google Search を使用すること。\n"
        "3. 日程ごとのタイムライン形式で、移動手段と所要時間を明記したプランを出力すること。"
    ),
    tools=[maps_mcp_toolset, google_search]
)
```

---

### Turn 5: 評価データセットの作成と振る舞い検証 (Phase 4: Evaluate)

#### 投入プロンプト

```text
エージェントの旅行計画品質、および Google Maps MCP / Google Search ツールの呼び出し妥当性を検証するため、`agents-cli eval` による評価を実施してください。

【評価手順】
1. 評価データセット (`eval/dataset.jsonl`) を作成し、代表的な旅行相談シナリオを2〜3件定義してください:
   - 例1: 「東京から箱根への日帰り旅行プラン（温泉と自然を満喫したい）」
   - 例2: 「福岡で名物グルメを巡る1泊2日の移動ルートと計画」
2. 評価基準:
   - 移動時間の見積もりが現実的であるか（Maps ツールが適切に呼ばれているか）
   - 最新の現地情報が反映されているか（Search ツールが活用されているか）
3. `agents-cli eval run` を実行し、LLM-as-judge による評価スコアを算出して結果を報告してください。
```

#### 解説とチェックポイント
- `pytest`（コード契約の検証）と `eval`（エージェントの振る舞い・計画の質の検証）を明確に区別して運用する。
- 評価スコアを確認し、ツールが正しく選択・併用されているかを評価する。

---

### Turn 6: Agent Runtimeへのデプロイと疎通確認 (Phase 5: Deploy)

#### 投入プロンプト

```text
評価結果に問題がなければ、Agent Runtime (Vertex AI Agent Engine) へのデプロイを実施してください。

【手順】
1. デプロイ前チェック:
   - `agents-cli info` でターゲットが `agent_runtime` に設定されていることを確認。
   - リモート Google Maps MCP サーバーへの接続権限および環境変数が整っているか確認。
2. デプロイの実行確認:
   - デプロイを実行してよいか確認メッセージを出し、承認後に `agents-cli deploy` を実行してください。
3. デプロイ後の確認:
   - デプロイ完了後、提供されるエンドポイントに対して疎通確認を行い、リモート環境で旅行プランが生成できることを確認してください。
```

#### 解説とチェックポイント
- Agent Runtime へのデプロイはバックグラウンドで進行するため、タイムアウトした場合は `agents-cli deploy --status` で進捗を確認する。
- デプロイ前に必ずユーザーの明示的な承認を得てから実行する。

---

## 4. Git 管理と運用のルール

1. **ブランチ運用**:
   - `main` ブランチへ直接コミットせず、`feature/travel-planner-mcp` などの作業ブランチを作成して作業する。
2. **コミットメッセージ**:
   - 英語で記述する (例: `feat: implement travel planner agent with Google Maps MCP and Google Search`).
3. **機密情報の除外**:
   - `.env` や Google Cloud クレデンシャルが Git に含まれていないことを必ずコミット前に確認する。
