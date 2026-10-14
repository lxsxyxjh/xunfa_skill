# 讯法法律工作流（xunfa-legal-workflow）

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Skill](https://img.shields.io/badge/Agent-Skill-orange.svg)](https://github.com/lxsxyxjh/xunfa_skill)

面向专业律师与法律智能体（AI Agent）的法律文书工作流规范与执行套件。支持专业文书起草、离线规则引擎预检、零篡改审查修订以及排版规范的标准 Word（DOCX）导出。

---

## 核心特性

1. **专业法律文书起草**
   - **全面诉求主张**：自动检索案涉合同付款节点与违约责任条款，合同明确由违约方承担的律师服务费、财产保全费、财产保全责任保险费等维权损失全量主张。
   - **严格证据照录**：引用合同条款、协议约定或生效裁判认定时，采用冒号加双引号（`：“……”`）一字不差精确照录原文，杜绝大意缩写与主观概括。
   - **单段紧凑三段论**：各争议焦点小标题下采用“客观事实陈述 —— 核心法条原文 —— 具体结论”在同一自然段内紧凑连贯推进，避免段落碎片化。
   - **严谨反 AI 味准则**：内置反 AI 味词库，全面阻断伪专业套话（`进一步印证`、`切断`、`证据链`、`形成完整证据链`、`至关重要`、`彻底落空`、`闭环`、`资金闭环证据`、`一揽子`、`焊死`、`锁定事实`、`铁证如山` 等），严禁“结论先行+冒号”总分结构与情绪化绝对化断言。

2. **本地规则预检与零篡改审查（离线引擎）**
   - **数据合规预检（`prepare`）**：
     - 自然人 18 位公民身份号码算法校验（GB 11643-1999 校验位及出生日期合法性）；
     - 法人 18 位统一社会信用代码算法校验（MOD 31-1 校验位）；
     - 联系电话（11 位手机号码及带区号固定电话）格式校验；
     - 银行卡号格式与公历日历有效性校验；
     - 成对标点符号闭合（`“”`、`‘’`、`《》`、`（）`）及未替换模板占位符检查；
     - 常见高频法律错别字自动识别与纠正建议。
   - **零篡改精准修订（`apply`）**：基于全文 SHA-256 哈希校验与精确字符偏移量，仅针对用户确认的审查项执行定向替换，未经确认内容 100% 原样保留。

3. **标准司法/商务排版 Word (DOCX) 导出**
   - 通过 `docx` 命令快速调用排版服务，将纯文本转换并导出为符合标准字号、行距与版式的 Word 文档。

4. **元典开放平台（Yuandian MCP）生态联动**
   - 支持与元典法学智库 MCP 联动，提供企业工商主体核实、涉诉背景穿透、现行有效法条权威详情查询与司法案例检索。

---

## 目录结构

```text
xunfa_skill/
├── SKILL.md                          # 智能体技能主规范文件（定义能力路由、执行工作流与写作规则）
├── README.md                         # 项目公开说明文档
├── references/
│   ├── document-drafting.md          # 诉状/答辩状/上诉状/判决书等各类文书固定模板与起草细则
│   ├── document-review.md            # 法律文书审查流程、反 AI 味排查细则与零篡改修订规范
│   └── law-retrieval.md              # 法律检索矩阵与法条/案例权威核验规范
├── scripts/
│   ├── xunfa.py                      # 统一 CLI 执行入口
│   ├── legal_review.py               # 本地规则校验、零篡改修订与 DOCX 导出核心引擎
│   └── yuandian_mcp.py               # 元典开放平台 MCP 客户端辅助脚本
└── tests/
    └── test_legal_review.py          # 本地核心引擎单元测试用例
```

---

## 快速上手

### 1. 运行环境准备
本项目核心规则引擎基于 Python 3 标准库构建，无强制第三方依赖；如需运行辅助脚本与测试，建议 Python 3.9 及以上版本：
```bash
python --version
```

### 2. 运行单元测试
```bash
python -m unittest discover tests
```

### 3. 本地规则预检（`prepare`）
将待审查或刚起草的文书保存为 UTF-8 文本文件，执行规则预检：
```bash
python scripts/xunfa.py prepare --text-file input.txt --output review-context.json
```
预检引擎将输出文档解析状态、`textSha256` 校验和以及发现的 `ruleIssues`（包括身份证/税号格式问题、未配对标点、错别字及 AI 味用词）。

### 4. 零篡改精准修订（`apply`）
根据预检生成的 `review-context.json` 和确认修正的 `accepted-issues.json` 进行精准字符替换：
```bash
python scripts/xunfa.py apply \
  --context review-context.json \
  --document-number 1 \
  --issues accepted-issues.json \
  --output corrected.txt
```

### 5. 导出标准 Word 文档（`docx`）
```bash
python scripts/xunfa.py docx --input corrected.txt --output "民事起诉状.docx"
```

---

## 配置说明

支持通过环境变量灵活配置外部服务（选填）：

| 环境变量 | 默认值 | 说明 |
| :--- | :--- | :--- |
| `DOCX_SERVICE_URL` | `http://1.14.120.187/file/exportLegalDocx` | 标准法律文书 DOCX 格式化导出服务接口地址 |
| `YUANDIAN_API_KEY` | *(空)* | 元典开放平台 API Key（亦可使用 `YUANDIAN_TOKEN`） |
| `YUANDIAN_MCP_URL` | `https://open.chineselaw.com/mcp` | 元典开放平台 MCP 服务接口地址 |

---

## 开源协议

本项目采用 [MIT 许可证](LICENSE)。
