# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import google_search
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.genai import types

# 環境変数の読み込み
load_dotenv()

MODEL = "gemini-3.8-flash"

# Google Maps MCP サーバーのエンドポイントおよび API キー取得
mcp_server_url = os.environ.get(
    "GOOGLE_MAPS_MCP_SERVER_URL",
    "https://mapstools.googleapis.com/mcp",
)
maps_api_key = os.environ.get("MAPS_API_KEY", "")

# Google Maps MCP ツールセット定義
maps_mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=mcp_server_url,
        headers={"X-Goog-Api-Key": maps_api_key},
    )
)

# ルートエージェント定義
root_agent = Agent(
    name="travel_planner_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "あなたはプロの旅行プランナーです。"
        "ユーザーの要望に基づいて実行可能で無理のない旅行計画を作成します。\n"
        "1. 目的地の位置情報、ルート、所要時間の確認には Google Maps MCP ツールを使用すること。\n"
        "2. 最新の観光地情報、おすすめスポット、営業時間、イベントの確認には Google Search を使用すること。\n"
        "3. 日程ごとのタイムライン形式で、移動手段と所要時間を明記したプランを出力すること。"
    ),
    tools=[maps_mcp_toolset, google_search],
)

app = App(
    root_agent=root_agent,
    name="app",
)
