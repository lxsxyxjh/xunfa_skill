# 法律文书生成

用户要求将纯文本生成标准法律文书 DOCX 时使用本流程。先将文书纯文本保存为 UTF-8 文件；起草结果只取 `txt_parse_docx` 代码块内的文本，不保留 Markdown 围栏或过程说明。

使用服务端标准设置时执行：

```bash
python scripts/xunfa.py docx --text-file "<临时目录>/document.txt" --output "<输出目录>/法律文书.docx"
```

用户明确要求调整格式时，将设置保存为 JSON 后传入：

```bash
python scripts/xunfa.py docx --text-file "<临时目录>/document.txt" --settings "<临时目录>/docx-settings.json" --output "<输出目录>/法律文书.docx"
```

`docx-settings.json` 可包含 `titleFont`、`bodyFont`、`titleSize`、`bodySize`、`lineHeightValue`、`indentValue`、`signatureAlign`、`dateAlign`、`bodyAlignMode`、`signaturePlaceholderNbspCount` 和 `datePlaceholderNbspCount`。未指定设置时由服务端应用标准格式。

命令只在收到标准 DOCX 二进制时写入输出路径；成功结果返回实际文件路径和字节数。需要复核生成文件时，按[法律文件解析](file-parsing.md)重新解析该 DOCX。
