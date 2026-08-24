# 法律文书检查

审查合同、诉状、判决书或其他法律文书时，找出能够根据原文或已核验法条确认的问题。输出聚焦具体错误和可执行修改，不把一般润色建议当作错误。本页的 `prepare` 已完成文书解析，文书检查直接使用本页流程。

## 工作流程

1. 同一案件的待审文书一次传入 `prepare`；文书包含法条引用或需要核验法律依据时，合并引用后运行一次 `laws`。检查按这个线性流程直接完成。
2. 用户粘贴文本时保存为当前任务私有临时 UTF-8 文件；用户提供文件时直接使用原文件。
3. 运行 `prepare` 取得每份文书的 `text`、`citations`、`ruleIssues` 和 `textSha256`，以返回的文本作为检查依据。
4. 阅读全文，确认脚本提示的错别字、标点、日期、号码、占位符和结构问题，并补充明确的事实、数值、序号和论述问题。检查上下文较长时，按 `text`、`citations` 和 `ruleIssues` 字段读取所需内容，避免一次读取整个 JSON。
5. 文书包含法条引用或需要核验法律依据时，合并引用后运行一次 `laws` 批量核验。自动提取的引用未调整时使用 `--context`；人工补充或修正引用后使用 `--queries`。
6. 交付已确认的问题和未核实项。需要生成完整修正版时，在用户确认具体替换内容后运行 `apply`。

认证状态按[认证与安全](authentication.md)完成登录后重试原命令。`partial` 结果保留成功文书，并在结果中说明 `itemErrors`。检查上下文和结果文件放在当前任务私有临时目录。

## 命令

```bash
python scripts/xunfa.py prepare --files "<文件1绝对路径>" "<文件2绝对路径>" --output "<临时目录>/review-context.json"
python scripts/xunfa.py prepare --text-file "<UTF-8临时文本>" --output "<临时目录>/review-context.json"
python scripts/xunfa.py laws --context "<临时目录>/review-context.json" --output "<临时目录>/law-results.json"
python scripts/xunfa.py laws --queries "<临时目录>/law-queries.json" --output "<临时目录>/law-results.json"
```

每个法条查询包含 `lawName` 和 `articleNumber`。批量结果中的单项错误作为未核实项说明。

## 检查重点

- 法条：核对法名、条号、正文、版本和适用条件。引用现行法时采用名称精确且 `statusText=有效` 的检索结果；合同、协议等书名号内容不作为法条提交查询。
- 文字与结构：检查明确的错别字、病句、标点、必要栏目、序号和交叉引用错误。
- 事实与数值：检查文书内部可证明的主体、日期、金额、数量、证据编号冲突，以及单价、合计、比例、利息和期间等可由已载明前提核算的关系。
- 论述：检查事实、法律依据、请求和结论之间的明确矛盾或缺口。材料不足以判断时，标为待核实并说明需要的材料。

## 交付格式

按普通编号列出问题，并写明文书、类别、原文或位置、问题和建议修改。例如：

```text
1. 《起诉状.docx》，错别字
原文：“权力人”
建议修改：“权利人”

2. 《起诉状.docx》，事实错误
问题：两处付款日期不一致。
建议：根据付款凭证确认正确日期。
```

法条核验失败、解析失败或材料不足时，单列“未核实项”说明原因。未发现明确问题时，简要说明检查结果。

## 生成修正版

用户确认需要修正版后，为已确定替换值的问题生成 `accepted-issues.json`，其中保留 `textSha256` 并为每项填写 `apply`、`replacementStatus`、位置、原文和替换文本：

```json
{
  "textSha256": "<review-context.json 的 textSha256>",
  "issues": [
    {"apply": true, "replacementStatus": "ready", "start": 0, "end": 2, "original": "错字", "replacement": "正字"}
  ]
}
```

```bash
python scripts/xunfa.py apply --context "<临时目录>/review-context.json" --document-number <文书序号> --issues "<临时目录>/accepted-issues.json" --output "<输出路径>/修改后完整版本.txt"
```

`apply` 会校验上下文、原文和替换位置，并生成完整修正版。没有确定替换值的事实问题，先向用户确认后再生成修正版。
