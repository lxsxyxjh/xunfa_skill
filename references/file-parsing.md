# 文件解析

读取、解析、OCR、提取或总结任何用户上传文件时使用本流程。不得仅因文件扩展名、文件类型或文件不是法律材料而拒绝调用；先将原文件绝对路径传给客户端，再根据实际返回结果判断是否成功。PDF 是优先场景，包括可复制文本 PDF、扫描 PDF、图片型 PDF 和多份 PDF；doc、docx、图片、文本及其他用户文件同样使用本流程：

```bash
python scripts/xunfa.py parse --files "<文件1绝对路径>" "<文件2绝对路径>" --output "<临时目录>/parsed-files.json"
```

输出 JSON 的 `files` 按输入顺序保存，`status` 为 `ok` 或 `partial`。每项包含原文件路径、SHA-256 和服务端解析结果；读取 `result.textContent`、`result.error` 与 `result.ocrProvider`。

`partial` 或单项 `error`、空 `textContent` 都表示服务器解析失败。保留成功文件结果，向用户说明失败原因并询问是否改用本地 OCR。用户同意后，由 Agent 自行选择本地解析方式。

## OCR 配置

查询当前账户配置：

```bash
python scripts/xunfa.py ocr-status --output "<临时目录>/ocr-status.json"
```

用户提供百度 OCR API Key 和 Secret Key 时，先读取 `ocr-status` 结果。`data.hasKey=false` 时，将凭据 JSON 通过标准输入交给 `ocr-set`：

```json
{"apiKey":"<API Key>","secretKey":"<Secret Key>"}
```

```bash
python scripts/xunfa.py ocr-set --output "<临时目录>/ocr-set.json"
```

客户端从标准输入读取凭据并输出服务端状态。账户已有密钥时，`ocr-set` 返回当前状态，不覆盖现有配置。删除配置使用：

```bash
python scripts/xunfa.py ocr-delete --output "<临时目录>/ocr-delete.json"
```

PDF 和图片只由用户配置的百度 OCR 在服务器上识别；PDF 也可能包含直接提取的文本页和百度 OCR 页。服务器不提供本机 OCR 兜底。
