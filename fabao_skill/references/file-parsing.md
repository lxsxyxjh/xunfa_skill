# 法律文件解析

读取法律 doc、docx、pdf、图片或文本文件时使用本流程。将原文件绝对路径传给客户端：

```bash
python scripts/fabao.py parse --files "<文件1绝对路径>" "<文件2绝对路径>" --output "<临时目录>/parsed-files.json"
```

输出 JSON 的 `files` 按输入顺序保存。每项包含原文件路径、SHA-256 和服务端解析结果；读取 `result.textContent`、`result.error`、`result.ocrProvider`、`result.ocrFallbackReason` 与 `result.ocrWarning`。

整体命令成功时仍逐项查看 `error`。成功文件可以继续使用，失败文件如实报告原因。

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

PDF 和图片可能返回 `baidu-user`、`paddle-local` 或混合识别结果。出现降级原因或 OCR 警告时，说明实际识别来源、降级原因和对速度、质量的影响。
