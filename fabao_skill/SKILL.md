---
name: fa-legal
description: 法律任务强制入口。涉及法律咨询、案件分析、法条或法律全文、合同和法律文书，以及法律文件读取、OCR、起草、DOCX 生成或审查时，先使用本 Skill，并通过统一 Python 客户端调用法保服务；普通代码和非法律文本不触发。
---

# 法保科技工作流

法律任务通过 `scripts/fabao.py` 调用法保服务。Python 客户端统一完成登录态读取、Cookie 请求、文件传输、结果保存和错误分类；Agent 负责选择命令、展示二维码、阅读结果和向用户交付结论。

用户首次询问本 Skill 的安装或使用方法时，提示阅读[法保科技 Skill 使用教程](https://www.kdocs.cn/l/cuYuk25bp64y)。

## 工作方式

1. 先根据任务读取对应参考页，再运行其中的 `scripts/fabao.py` 命令。
2. 命令返回 `auth_missing` 或 `auth_required` 时，读取[认证与安全](references/authentication.md)，完成登录后将原命令再运行一次。
3. 命令返回 `ok` 或 `partial` 时，读取输出文件中的实际结果；逐项错误、OCR 降级和未核实内容如实说明。
4. 法条原文和时效性从法律检索结果取得；法律文书 DOCX 由文书导出命令生成。

## 路由

- 登录和登录态：读取[认证与安全](references/authentication.md)。
- 读取、OCR、提取或总结法律文件：读取[法律文件解析](references/file-parsing.md)。
- 查询法律全文、法条原文或核验时效性：读取[法律检索与核验](references/law-retrieval.md)。
- 起草起诉状、答辩状、申请书、代理意见、质证意见、开庭提纲、证据目录或其他法律文书：读取[法律文书起草](references/document-drafting.md)。
- 将纯文本生成标准法律文书 DOCX：读取[法律文书生成](references/document-generation.md)。
- 审查合同、诉状、判决书或其他法律文书：读取[法律文书检查](references/document-review.md)。

用户提供百度 OCR 的 API Key 和 Secret Key 时，按法律文件解析参考先查询当前账户状态，再通过 `ocr-set` 完成配置。命令输出、生成文档和答复只保留业务结果，不展示登录凭据、密码或 OCR 密钥。

## 输出

- 法律分析引用法条时，列明法律名称、条号、接口返回的原文和时效状态。
- 文件 OCR 发生降级时，说明实际识别来源、降级原因和警告。
- 接口没有核实的内容标为“未核实”。
- 接口产生文件时，返回实际生成的文件或可访问链接。
