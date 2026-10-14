#!/usr/bin/env python3
import argparse
import json
import os
import sys
import requests

ENV_PATH = os.environ.get("HERMES_ENV_PATH", ".env")
YUANDIAN_URL = os.environ.get("YUANDIAN_MCP_URL", "https://open.chineselaw.com/mcp")


def load_yuandian_token() -> str:
    token = os.environ.get("YUANDIAN_TOKEN") or os.environ.get("YUANDIAN_API_KEY")
    if token:
        return token if token.startswith("Bearer ") else f"Bearer {token}"
    if os.path.exists(ENV_PATH):
        try:
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    if "YUANDIAN" in line and "=" in line:
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            return val if val.startswith("Bearer ") else f"Bearer {val}"
        except Exception:
            pass
    return ""


YUANDIAN_TOKEN = load_yuandian_token()


class YuandianMCPClient:
    def __init__(self, url: str = YUANDIAN_URL, token: str = YUANDIAN_TOKEN):
        self.url = url
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if token:
            self.headers["Authorization"] = token
        self.session_id = None

    def ensure_session(self) -> None:
        if self.session_id:
            return
        init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "xunfa-legal-workflow", "version": "1.0.0"},
            },
        }
        resp = requests.post(self.url, headers=self.headers, json=init_payload, timeout=30)
        resp.raise_for_status()
        self.session_id = resp.headers.get("mcp-session-id")
        if self.session_id:
            self.headers["mcp-session-id"] = self.session_id

    def call_tool(self, tool_name: str, arguments: dict) -> dict:
        self.ensure_session()
        payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }
        resp = requests.post(self.url, headers=self.headers, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()


def main() -> int:
    parser = argparse.ArgumentParser(description="元典开放平台 MCP 工具直连调用器")
    parser.add_argument("tool", help="元典工具名称，如 yuandian_search_legal_articles / yuandian_search_companies / yuandian_hall_detect")
    parser.add_argument("args_json", nargs="?", default="{}", help="JSON 格式的参数字典")
    args = parser.parse_args()

    client = YuandianMCPClient()
    parsed_args = json.loads(args.args_json)
    result = client.call_tool(args.tool, parsed_args)
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
