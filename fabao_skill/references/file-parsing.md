# 文件解析

读取 doc、docx、pdf、图片或文本文件时使用本流程。将原文件绝对路径传给客户端：

```bash
python scripts/fabao.py parse --files "<文件1绝对路径>" "<文件2绝对路径>" --output "<临时目录>/parsed-files.json"
```

输出 JSON 的 `files` 按输入顺序保存，`status` 为 `ok` 或 `partial`。每项包含原文件路径、SHA-256 和服务端解析结果；读取 `result.textContent`、`result.error` 与 `result.ocrProvider`。

`partial` 或单项 `error`、空 `textContent` 都表示服务器解析失败。保留成功文件结果，向用户说明失败原因并询问是否改用本地 OCR。用户同意后，由 Agent 自行选择本地解析方式。

## OCR 配置

查询当前账户配置：

```bash
python scripts/fabao.py ocr-status --output "<临时目录>/ocr-status.json"
```

用户提供百度 OCR API Key 和 Secret Key 时，先读取 `ocr-status` 结果。`data.hasKey=false` 时，将凭据 JSON 通过标准输入交给 `ocr-set`：

```json
{"apiKey":"<API Key>","secretKey":"<Secret Key>"}
```

```bash
python scripts/fabao.py ocr-set --output "<临时目录>/ocr-set.json"
```

客户端从标准输入读取凭据并只输出脱敏后的服务端结果。账户已有密钥时，`ocr-set` 返回当前状态，不覆盖现有配置。删除配置使用：

```bash
python scripts/fabao.py ocr-delete --output "<临时目录>/ocr-delete.json"
```

PDF 和图片只由用户配置的百度 OCR 在服务器上识别；PDF 也可能包含直接提取的文本页和百度 OCR 页。服务器不提供本机 OCR 兜底。
