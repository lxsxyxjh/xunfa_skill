# 法律文件解析

读取法律 doc、docx、pdf、图片或文本文件时使用本流程。先按 [认证与安全](authentication.md) 获取登录态。

检查法律文书时不手工执行本页请求，直接使用 `scripts/legal_review.py prepare`；本页只作为脚本失败后的接口参考。

## 接口

`POST /file/MultipartFiles/uploadAndParse`

Content-Type：`multipart/form-data`

- `files`：一个或多个文件，必填；保留原始文件名和扩展名。
- `outputFormat`：docx 可传 `markdown`、`html` 或 Pandoc 的 `plain`，默认 `markdown`；其他类型返回提取文本。
- `needText`：固定传 `true`。
- `saveRecord`：固定传 `false`，不写文件记录数据库。

文件仍会先上传到服务器磁盘；`saveRecord=false` 只是不写数据库记录。单文件大小由服务端参数 `fileMaxSizeMB` 控制，读取失败时默认上限为 100MB。

## 读取响应

成功时 `data` 是逐文件结果数组。逐项检查：

- `fileName`、`fileSize`、`fileExtension`：原文件信息。
- `url`：服务器文件访问地址。
- `textContent`：解析文本。
- `error`：当前文件失败原因，空值表示成功。
- `ocrProvider`：`none` 表示未用 OCR，`baidu-user` 表示用户自己的百度 OCR，`paddle-local` 表示服务端本地 PaddleOCR。
- `ocrFallbackReason`：常见值为 `USER_CREDENTIAL_NOT_CONFIGURED` 或 `BAIDU_USER_CREDENTIAL_FAILED`。
- `ocrWarning`：需要向用户说明的 OCR 警告。

整体 `code=="1"` 不代表每个文件都成功。继续处理成功文件，只报告失败项目的具体原因。OCR 元数据非空时说明实际识别来源和降级原因，不展示凭据。

## 解析路由

- docx：按文件头识别 OOXML，优先调用 Pandoc；结果为空时读取 `word/afchunk.mht`。
- doc：按文件头识别 OLE2，提取段落和表格。
- PDF：先用 PDFBox 提取文本；去除空白和控制字符后，平均每页不足 20 个字符时进入 OCR。
- PDF OCR：最大页数由“pdf解析最大页数”控制，读取失败时默认 100 页。
- 图片：支持 jpg、jpeg、png、bmp、gif、webp、tif、tiff，并调用 OCR。
- 文本：支持服务端配置的文本扩展名及 txt，返回纯文本。

纯图片组成的 doc 或 docx 当前不会自动对嵌入图片执行 OCR。内容为空时如实报告，不用通用文档工具猜测内容。

## OCR 降级

PDF 和图片 OCR 按以下顺序执行：

1. 用户已配置百度凭据时，使用用户自己的额度。
2. 用户未配置凭据时，使用服务端本地 PaddleOCR。
3. 用户百度 OCR 调用失败时，自动使用服务端本地 PaddleOCR，并返回降级原因和警告。

服务端不使用平台公共百度密钥。用户可通过网站账户设置或在 Agent 对话中提供自己的百度 OCR 凭据：

- `GET /user/ocrCredential`：只查询脱敏末四位和验证状态。
- `PUT /user/ocrCredential`：验证后保存，密钥加密存储。
- `DELETE /user/ocrCredential`：删除凭据并清理该用户的 token 与失败状态。

当用户在对话或接口参数中提供完整的 API Key 和 Secret Key 时，先调用 `GET /user/ocrCredential` 查询当前账户。仅在 `data.hasKey=false` 时调用 `PUT /user/ocrCredential` 传入密钥；接口会先验证百度凭据，成功后写入数据库，失败时不保存。已有凭据时不覆盖。

## 故障处理

- 空文件会被忽略；文件名异常、文件超限或解析异常从对应项目的 `error` 读取。
- multipart 上传失败时检查本机代理、网络和文件读取权限，并报告实际错误，不自动重试。
- 上传环境不能正确处理中文文件名时，可以复制为临时英文文件名上传，但答复中仍使用原始文件名。
- 接口持续不可用时报告 HTTP 状态和响应消息，不切换到通用解析工具。
