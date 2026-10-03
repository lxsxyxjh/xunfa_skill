# 寻法（xunfa-legal-workflow）Skill

寻法（`xunfa-legal-workflow`）为文件解析和法律工作提供统一入口。它通过寻法服务完成文件解析、法条检索、法律文书 DOCX 导出和登录态管理；文书检查还会结合本地规则识别明确的形式错误。

日常使用由 Codex 自动路由到 `SKILL.md`。本 README 面向维护者和需要手动运行客户端的人，说明项目结构、可用命令和本地校验方式；具体任务规则以对应的 `references/` 文档为准。

## 项目结构

```text
xunfa_skill/
├── SKILL.md                     Skill 入口、路由和共享约束
├── scripts/
│   ├── xunfa.py                 命令行入口
│   └── legal_review.py          客户端、解析和文书检查实现
├── references/
    ├── authentication.md        微信扫码与账号密码登录
    ├── file-parsing.md          文件解析与 OCR 配置
    ├── law-retrieval.md         法条检索和时效核验
    ├── document-drafting.md     法律文书起草
    ├── document-generation.md   DOCX 导出
    └── document-review.md       法律文书检查与修正版生成
└── tests/
    └── test_legal_review.py     文书修订文本测试
```

`scripts/xunfa.py` 是稳定的命令入口，实际实现位于 `scripts/legal_review.py`。从项目根目录运行命令；Windows 使用 `python`，macOS 和 Linux 通常使用 `python3`：

```powershell
python scripts/xunfa.py --help
```

## 使用前准备

- Python 3.9 或更高版本；项目仅使用标准库，无需安装第三方依赖。
- 默认服务地址为 `https://xunfakeji.com`。只有需要连接本机开发服务时，才为命令传入 `--base-url`。
- 业务命令需要登录态。登录成功后，客户端将会话保存到当前用户目录 `.xunfa/auth.json`，不会把密码或 OCR 密钥写入项目。
- 输入文件使用绝对路径；输出路径必须是尚不存在的新文件。临时 JSON、文本和二维码建议放到当前任务的私有临时目录。

## 登录

推荐微信扫码登录：

```powershell
python scripts/xunfa.py auth-qr-start --output "<临时目录>/xunfa-login.png"
python scripts/xunfa.py auth-qr-wait --uuid "<auth-qr-start 返回的 uuid>"
```

第一条命令会生成二维码 PNG。展示该图片并完成扫码后，再执行第二条命令；该命令通过 SSE 等待扫码通知，不会轮询登录接口。也可以在可交互终端使用账号密码登录：

```powershell
python scripts/xunfa.py auth-password --username "<账号>" --password-prompt
```

业务命令返回 `auth_missing` 或 `auth_required` 时，完成登录后重试原命令一次。完整流程见 [认证与安全](references/authentication.md)。

## 常用命令

| 场景 | 命令 | 参考文档 |
| --- | --- | --- |
| 解析 doc、docx、pdf、图片或文本文件 | `parse --files "<绝对路径>" --output "<临时目录>/parsed-files.json"` | [文件解析](references/file-parsing.md) |
| 批量核验原文中明确出现的法条 | `laws --queries "<临时目录>/law-queries.json" --output "<临时目录>/law-results.json"` | [法律检索与核验](references/law-retrieval.md) |
| 按完整法名查询法条 | `law-exact --input "<请求.json>" --output "<结果.json>"` | [法律检索与核验](references/law-retrieval.md) |
| 将法律文书纯文本导出为 DOCX | `<文书纯文本> \| python scripts/xunfa.py docx --output "<输出.docx>"` | [法律文书生成](references/document-generation.md) |
| 生成法律文书检查上下文 | `prepare --files "<绝对路径>" --output "<临时目录>/review-context.json"` | [法律文书检查](references/document-review.md) |
| 根据已确认的问题生成修正版文本 | `apply --context "<检查上下文.json>" --document-number 1 --issues "<确认问题.json>" --output "<修正版.txt>"` | [法律文书检查](references/document-review.md) |

上表只列出命令骨架。请求 JSON 的结构、OCR 配置和文书检查的完整执行顺序，请读取相应参考文档，不要依据本表猜测参数内容。

## 输出与错误处理

客户端在标准输出输出简短 JSON 状态，详细结果写入 `--output` 指定的文件。常见状态如下：

| 状态 | 含义 | 处理方式 |
| --- | --- | --- |
| `ok` | 请求或处理已完成 | 读取输出文件中的实际结果 |
| `partial` | 部分文件或法条未完成 | 保留成功结果，并读取 `itemErrors` 说明未完成项 |
| `auth_missing` / `auth_required` | 没有可用登录态或登录态失效 | 登录后重试原命令一次 |
| `input_failed` | 输入、输出路径或 JSON 格式不符合要求 | 修正参数或换用新的输出路径 |
| `request_failed` | 服务请求未完成或响应格式异常 | 如实报告错误，不把未核验内容当作结果 |

文书检查的 `prepare` 结果中的 `ruleIssues` 是候选问题，提交给用户前仍应结合原文复核。Agent 根据原文整理明确的法条查询项，法条引用以检索结果中的法名、条号、原文和时效状态为准。

## 每日版本检查与手动更新

每个自然日首次执行实际业务命令时，客户端会在最多 3 秒内静默检查一次远端版本。检查结果不会影响业务处理；只有本地版本可以安全快进到上游版本时，成功 JSON 才会包含 `updateNotice`。没有更新、网络不可用、Git 不可用、本地领先或历史分叉时均不提示。

Agent 读取到 `updateNotice` 后，应先交付本次业务结果，再附带其中的更新提示。客户端不会自动更新 Skill。

用户明确要求“更新寻法”时，先在 Skill 根目录检查工作区状态并刷新远端；仅在工作区干净且可快进时执行：

```powershell
git pull --ff-only
```

存在未提交改动、本地领先或历史分叉时停止更新并报告原因。不要使用 `reset`、`rebase`、`stash`、强制覆盖或自动提交。

## 维护与校验

在项目根目录执行：

```powershell
python -X utf8 -m py_compile scripts/xunfa.py scripts/legal_review.py
python -X utf8 scripts/xunfa.py --help
python -X utf8 -m unittest discover -s tests -v
git diff --check
```

再使用当前机器安装的 Skill Creator 中的 `scripts/quick_validate.py` 校验本目录。前三项检查 Python 语法、CLI 装配和文书修订；Skill 校验检查前置元数据与未完成脚手架；`git diff --check` 检查已改动文件的空白错误。它们都不替代带真实账号、真实文件和服务端接口的端到端验证。

## 维护原则

- 把任务路由、共享安全边界保留在 `SKILL.md`，把特定任务的流程和模板放在对应的 `references/`，避免在多处复制同一规则。
- 新增规则前先确认它是否改变 Agent 的实际决策。一次性失败、文风偏好或通用常识不宜写成强制要求。
- 涉及外部服务的命令应保留明确的输入、输出和停止条件；敏感凭据只经标准输入或本地登录态传递。
