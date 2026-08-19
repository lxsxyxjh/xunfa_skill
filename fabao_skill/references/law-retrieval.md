# 法律检索与核验

查询法律全文、法条原文或时效性时使用本流程。先按 [认证与安全](authentication.md) 获取登录态。

## 批量查询

文书检查或同一任务需要核验多个法条时，优先一次调用：

`POST /laws/searchByLawBatch`

Content-Type：`application/json`

请求体直接传 JSON 数组，最多 50 项；每项必须提供法名和条号，可以混合任意不同法律、普通条文和“条之一”等增设条文：

```json
[
  {"lawName":"中华人民共和国民法典","articleNumber":"第一千零八十六条"},
  {"lawName":"中华人民共和国家庭教育促进法","articleNumber":"第二十条"},
  {"lawName":"中华人民共和国刑法","articleNumber":"第二百二十四条之一"}
]
```

响应 `data` 按输入顺序逐项返回：

- `index`：输入数组序号。
- `requestedLawName`、`requestedArticleNumber`：原始请求值。
- `normalizedLawName`、`normalizedArticleNumber`：后端规范化后的值。
- `results`：与单条查询相同的法条结果数组。
- `error`：当前项的参数错误、“未找到法律”或“未找到指定条文”；单项错误不影响其他项，也不得触发整个批次重试。

`scripts/legal_review.py laws` 会按“法名＋条号”去重后提交一个 List。若接口返回“候选版本过多，未完整核验指定条文”，将该项标为未核实，不能据此声称法条不存在。文书检查优先复用脚本的批量查询结果，避免逐条重复请求。

## 已知法名

`POST /laws/searchByLaw`

Content-Type：`application/x-www-form-urlencoded`

- `lawName`：必填。支持完整名称、带或不带书名号的名称，以及后端已配置的简称。
- `articleNumber`：可选。支持“第二十条”“第20条”“第２０条”“20”“二十”及“第二百二十四条之一”等增设条文。

接口按去除书名号后的完整标题精确匹配，不用于主题词或残缺法名搜索。正常返回项只能是该完整标题的不同版本，不应出现标题不同的司法解释、修正案说明或其他法律文件。

响应 `data` 为数组，常用字段包括：

- `lawId`、`url`、`lawName`、`typeField`。
- `status`：`1` 废止、`2` 已修改、`3` 有效、`4` 尚未生效。
- `statusText`、`office`、`publish`、`effective`。
- 未传条号时读取 `fullText`。
- 传条号时读取 `articleNumber` 和 `articleText`。

按法名查询已经返回最终正文，不再根据 `lawId` 重复请求。条文未命中的版本不会出现在结果数组中；空数组表示法名与条号组合未命中。

同名多版本按精确名称、时效状态和发布日期判断。引用现行法时只使用名称精确且 `statusText=有效` 的版本；已修改、废止或尚未生效必须明确提示，并在存在有效版本时给出有效版本。

返回多条记录时，先保留并核对每条记录的 `lawId`、`lawName`、`statusText`、`publish` 和 `effective`，再选择版本：

1. 向用户说明实际返回的版本数量和选中版本的上述字段。
2. 不得把接口没有返回的文件描述成“干扰项”，不得自行声称排除了某个司法解释或其他文件。
3. 返回项的 `lawName` 与规范化后的完整法名不一致时，报告接口数据异常并保留原始字段，不自行过滤或改名。
4. 同时存在多个有效版本且正文不一致时，不静默选取；列出差异所涉及的版本信息，并说明需要进一步确认。

## 不知道完整法名

`POST /laws/search`

Content-Type：`application/x-www-form-urlencoded`

- `keywords`：一个或多个非空主题关键词，可以重复传递。
- `pageNumber`：默认 1。
- `pageSize`：默认 10。

响应 `data` 为分页对象，常用字段为 `total`、`current`、`size`、`records`。候选记录包含 `id`、`title`、`typeField`、`status` 和最多 5 个 `textList` 命中片段。

该接口只用于发现候选法律。`textList` 是检索片段，不能作为法条原文引用。确定候选 `title` 后，必须调用 `/laws/searchByLaw` 获取全文或指定条文。

## 已有可信 lawId

`POST /laws/getLawText`

Content-Type：`application/x-www-form-urlencoded`

- `lawId`：必填，只用于调用方已经持有可信 ID 的场景。
- `articleNumber`：可选，格式与按法名查询相同。

不传条号时，读取单元素结果中的 `fullText`；传条号且命中时，读取 `articleNumber` 和 `articleText`。ID 不存在或条文未命中时返回空数组。

## 核验规则

1. 找出任务中的全部法律引用，按“法名＋条号”去重。
2. 文书检查中的已知法名查询无论数量多少都调用一次批量接口；其他任务两条以上时使用批量接口，不循环调用单条接口。
3. 不知道完整法名时先发现候选，确认名称后再加入批量查询。
4. 逐字核对法名、条号、款、项、正文、数字和标点。
5. 输出法律名称、规范条号、接口原文、时效状态和详情页链接。
6. 接口没有返回的内容标为“未核实”，禁止用模型记忆补齐。

检索到多个版本而无法确定适用时间时，列出版本、发布日期、施行日期和状态，并结合用户给出的事件时间说明仍需确认的适用版本。
