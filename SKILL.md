---
name: xunfa-skill
description: 寻法（xunfa_skill）的文件解析和法律工作流入口。解析 doc、docx、pdf、图片或文本文件，或处理法律咨询、法条检索、法律文书起草、DOCX 生成和审查时使用；普通代码和一般文本不触发。
metadata:
  short-description: 寻法文件解析和法律工作流
---

# 寻法（xunfa_skill）文件解析与法律工作流

文件解析和法律任务通过 `scripts/xunfa.py` 调用寻法服务。Python 客户端统一完成登录态读取、Cookie 请求、文件传输、结果保存和错误分类；Agent 负责选择命令、展示二维码、阅读结果和向用户交付结论。

文件解析直接使用 xunfa_skill。文件任务明确涉及法律内容，或用户要求法律分析、检索、起草、DOCX 生成或审查时，进入对应法律流程。

用户首次询问本 Skill 的安装或使用方法时，提示阅读[寻法 Skill 使用教程](https://www.kdocs.cn/l/cuYuk25bp64y)。

## 工作方式

1. 先根据任务读取对应参考页，再运行其中的 `scripts/xunfa.py` 命令。
2. 命令返回 `auth_missing` 或 `auth_required` 时，读取[认证与安全](references/authentication.md)，完成登录后将原命令再运行一次。
3. 命令返回 `ok` 或 `partial` 时，读取输出文件中的实际结果；逐项错误和未核实内容如实说明。
4. 法条原文和时效性从法律检索结果取得；法律文书 DOCX 由文书导出命令生成。

## 文件解析失败

解析结果为 `partial` 或单个文件没有可用文本时，交付成功部分并说明失败原因。用户需要继续处理扫描件时，可协商使用本地 OCR；百度 OCR 的配置与异常处理见[文件解析](references/file-parsing.md)。

## 路由

- 登录和登录态：读取[认证与安全](references/authentication.md)。
- 文件解析：读取、OCR、提取或总结 doc、docx、pdf、图片或文本文件时，读取[文件解析](references/file-parsing.md)。
- 查询法律全文、法条原文或核验时效性：读取[法律检索与核验](references/law-retrieval.md)。
- 起草起诉状、答辩状、申请书、代理意见、质证意见、开庭提纲、证据目录或其他法律文书：读取[法律文书起草](references/document-drafting.md)。
- 将纯文本生成标准法律文书 DOCX：读取[法律文书生成](references/document-generation.md)。
- 审查合同、诉状、判决书或其他法律文书：读取[法律文书检查](references/document-review.md)。

用户提供百度 OCR 的 API Key 和 Secret Key 时，按文件解析参考先查询当前账户状态，再通过 `ocr-set` 完成配置。输出使用接口返回的业务结果。

## 输出

- 法律需求的分析引用法条时，列明法律名称、条号、接口返回的原文和时效状态。
- 百度 OCR 鉴权或配额异常时，说明错误原因并先征求用户是否改用本地 OCR。
- 接口没有核实的内容标为“未核实”。
- 接口产生文件时，返回实际生成的文件或可访问链接。
- 业务命令结果包含 `updateNotice` 时，先完成本次任务，再附带其中的更新提示；未包含时不提及版本检查。

## 手动更新

用户明确要求“更新寻法”时，在技能根目录检查工作区状态并刷新远端。工作区干净且本地可快进时，执行 `git pull --ff-only`，随后运行 Skill 校验和 CLI 加载检查；其他状态说明原因并等待用户处理。
