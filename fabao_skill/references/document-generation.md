# 法律文书生成

用户要求将纯文本生成标准法律文书 docx 时使用本流程。先按 [认证与安全](authentication.md) 获取登录态。

## 准备正文

- 按行组织纯文本，第一行作为标题。
- 使用法律文书起草流程形成正文时，直接取单个 `txt_parse_docx` 代码块内部的完整纯文本作为 `text`，不保留代码块围栏或其他 Markdown 标记。未要求生成 DOCX 时，只交付该代码块，不调用本接口。
- 生成前确认文书类型、当事人信息、正文、落款和日期。
- 涉及法条时先按 [法律检索与核验](law-retrieval.md) 取得原文与时效性。
- 不在正文中补写用户未提供且无法核实的事实。

## 接口

`POST /file/exportLegalDocx`

Content-Type：`application/json`

请求字段：

- `text`：必填，按行组织的文书纯文本。
- `fileName`：可选；缺省时取正文首行。非法文件名字符会替换为 `-`，并自动补 `.docx` 后缀。
- `settings`：可选，用于覆盖标准格式设置。

普通文书设置包括 `titleFont`、`bodyFont`、`titleSize`、`bodySize`、`lineHeightValue`、`indentValue`、`enableBoldKeywords`、`signatureAlign`、`dateAlign`、`bodyAlignMode`、`signaturePlaceholderNbspCount`、`datePlaceholderNbspCount`。

法院文书设置包括 `judgmentTitleFont`、`judgmentBodyFont`、`judgmentTitleSize`、`judgmentBodySize`、`judgmentLineHeightValue`、`judgmentIndentChars`。

除非用户明确要求，使用服务端标准设置，不自行覆盖版式。签名和日期默认保留手写空白区；需要输出实体文本时，将对应占位数量设为 0。

## 判断响应

成功响应满足：

- Content-Type 为 `application/vnd.openxmlformats-officedocument.wordprocessingml.document`。
- 响应体为 docx 二进制。
- Content-Disposition 包含最终文件名。

失败响应由全局异常处理包装为 JSON。即使 HTTP 状态为 200，只要 Content-Type 或正文表明是 JSON，就必须读取 `code` 和 `msg`，不得把响应保存为 docx。

## 复核文件

生成结果使用 html-docx 的 AltChunk 结构，正文位于 `word/afchunk.mht`，`document.xml` 只有引用属于正常现象。Word 和 WPS 可以正常打开。

需要读取或复核生成结果时，调用 [法律文件解析](file-parsing.md)，不要使用只读取 `document.xml` 的通用 docx 解析器。仅在本技能生成的文件无法上传解析时，才可读取 `word/afchunk.mht` 作为本地兜底。
