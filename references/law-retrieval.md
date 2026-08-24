# 法律检索与核验

查询法律全文、法条原文或时效性时使用本流程。先运行对应的 `scripts/xunfa.py` 命令；命令返回认证状态时按[认证与安全](authentication.md)完成登录并重试一次。

## 批量核验已知法条

同一任务有两条以上已知法条时，将查询数组保存到当前任务私有临时目录：

```json
[
  {"lawName":"中华人民共和国民法典","articleNumber":"第一千零八十六条"},
  {"lawName":"中华人民共和国刑法","articleNumber":"第二百二十四条之一"}
]
```

执行一次批量查询：

```bash
python scripts/xunfa.py laws --queries "<临时目录>/law-queries.json" --output "<临时目录>/law-results.json"
```

客户端按“法名＋条号”去重，单次最多 50 项。结果按输入顺序返回；逐项读取 `results`、`error`、规范化法名和条号。单项未命中或参数错误作为未核实项继续处理。

## 单项查询

完整法名查询将请求对象保存为 JSON：

```json
{"lawName":"中华人民共和国民法典","articleNumber":"第五百零九条"}
```

```bash
python scripts/xunfa.py law-exact --input "<临时目录>/law-exact.json" --output "<临时目录>/law-exact-result.json"
```

不知道完整法名时，保存关键词、页码和页大小：

```json
{"keywords":["民间借贷"],"pageNumber":1,"pageSize":10}
```

```bash
python scripts/xunfa.py law-search --input "<临时目录>/law-search.json" --output "<临时目录>/law-search-result.json"
```

已有可信 `lawId` 时使用：

```json
{"lawId":1,"articleNumber":"第五百零九条"}
```

```bash
python scripts/xunfa.py law-id --input "<临时目录>/law-id.json" --output "<临时目录>/law-id-result.json"
```

## 核验与输出

引用现行法时使用名称精确且 `statusText=有效` 的结果。逐字核对法名、条号、款、项、正文、数字和标点；检索结果没有返回的内容标为“未核实”。

主题检索的 `textList` 只用于发现候选法律。确定完整法名后，再运行 `law-exact` 取得可引用的原文与时效状态。
