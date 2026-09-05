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

import pytest
from google.adk.tools import google_search
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from app.agent import root_agent, MODEL


def test_agent_model() -> None:
    # モデル設定の検証
    assert MODEL == "gemini-3.8-flash"
    assert root_agent.model.model == "gemini-3.8-flash"


def test_agent_instruction() -> None:
    # 指示プロンプトの検証
    instruction = root_agent.instruction
    assert "旅行" in instruction
    assert "Google Maps" in instruction or "Maps" in instruction
    assert "Google Search" in instruction or "Search" in instruction


def test_tools_registered() -> None:
    # ツール登録の検証
    tools = root_agent.tools
    assert len(tools) >= 2

    # McpToolset と google_search の存在確認
    has_mcp_toolset = any(isinstance(tool, McpToolset) for tool in tools)
    has_google_search = google_search in tools or any(
        getattr(tool, "__name__", "") == "google_search" for tool in tools
    )

    assert has_mcp_toolset, "McpToolset が登録されていない"
    assert has_google_search, "google_search が登録されていない"


def test_maps_mcp_toolset_configuration() -> None:
    # Maps MCP ツールセットの設定検証
    mcp_tools = [tool for tool in root_agent.tools if isinstance(tool, McpToolset)]
    assert len(mcp_tools) > 0, "McpToolset が存在しない"

    mcp_tool = mcp_tools[0]
    params = mcp_tool.connection_params
    assert isinstance(params, StreamableHTTPConnectionParams)
    assert "mapstools.googleapis.com" in params.url
    assert "X-Goog-Api-Key" in params.headers
