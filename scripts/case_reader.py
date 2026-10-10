#!/usr/bin/env python3
"""扫描版 PDF 原生多模态解析器 (极简无冗余、单次请求多附件打包投递)"""
import base64
import os
import sys
import requests

ENV_PATH = "C:/Users/chengfeng/AppData/Local/hermes/.env"
API_URL = "http://43.130.251.44:8317/v1/chat/completions"
MODEL = "gemini-3.8-flash-high"


def load_api_key() -> str:
    key = os.environ.get("HERMES_CUSTOM_GEMINI_FANDAILI_API_KEY", "").strip()
    if key:
        return key
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as fh:
            for line in fh:
                if "HERMES_CUSTOM_GEMINI_FANDAILI_API_KEY" in line and "=" in line:
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("Missing API Key")


def parse_pdfs(pdf_paths: list[str], prompt: str = "请完整提取以下各个文件的全部文字信息、印章、手写签名、金额及日期要素：") -> str:
    api_key = load_api_key()
    valid_files = []
    for p in pdf_paths:
        if p.startswith("-"):
            continue
        if os.path.isdir(p):
            for entry in sorted(os.listdir(p)):
                full = os.path.join(p, entry)
                if os.path.isfile(full) and full.lower().endswith(".pdf"):
                    valid_files.append(full)
        elif os.path.isfile(p) and p.lower().endswith(".pdf"):
            valid_files.append(p)
    if not valid_files:
        return "未找到有效的 PDF 文件"

    content = [{"type": "text", "text": prompt}]
    for idx, path in enumerate(valid_files, 1):
        with open(path, "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode("utf-8")
        fname = os.path.basename(path)
        content.append({"type": "text", "text": f"\n\n====================\n【附件 {idx} / 文件名称：{fname}】\n===================="})
        content.append({"type": "image_url", "image_url": {"url": f"data:application/pdf;base64,{b64}"}})

    resp = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": MODEL, "messages": [{"role": "user", "content": content}]},
        timeout=240,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: case_reader.py <file1.pdf> [file2.pdf ...]")
        sys.exit(1)
    result = parse_pdfs(sys.argv[1:])
    sys.stdout.reconfigure(encoding="utf-8")
    print(result)
