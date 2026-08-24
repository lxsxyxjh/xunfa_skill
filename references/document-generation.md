# 法律文书生成

用户要求将纯文本生成标准法律文书 DOCX 时使用本流程。将已起草的完整文书纯文本通过标准输入交给 `docx` 命令，客户端直接提交给文书导出接口。

使用服务端标准设置时执行：

```bash
$documentText | python scripts/xunfa.py docx --output "<输出目录>/法律文书.docx"
```

用户明确要求调整格式时，将设置保存为 JSON 后传入：

```bash
$documentText | python scripts/xunfa.py docx --settings "<临时目录>/docx-settings.json" --output "<输出目录>/法律文书.docx"
```

`docx-settings.json` 可包含 `titleFont`、`bodyFont`、`titleSize`、`bodySize`、`lineHeightValue`、`indentValue`、`signatureAlign`、`dateAlign`、`bodyAlignMode`、`signaturePlaceholderNbspCount` 和 `datePlaceholderNbspCount`。未指定设置时由服务端应用标准格式。

命令收到标准 DOCX 二进制后写入输出路径并交付生成的文件。需要复核时，按[法律文件解析](file-parsing.md)重新解析该 DOCX。
