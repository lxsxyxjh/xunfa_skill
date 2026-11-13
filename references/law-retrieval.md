# 法律检索与核验规范

在起草或审查法律文书涉及企业主体查询、法条引用、法律效力核验及类案检索时，必须严格遵守本规范。

## 一、元典开放平台 MCP（`yuandian-open-platform`）核心检索矩阵

凡涉及查企业、查法条、查案例、法律幻觉校验，统一优先调用元典 MCP 工具（与本技能共同使用）。工具名前缀以各 agent 实际注册的 MCP 工具列表为准，同一服务器 `yuandian-open-platform` 在不同 agent 中的工具前缀可能不同：

1. **查企业（主体信息与涉诉背景）**：
   - 检索企业候选/获取 ID 与统一社会信用代码：`mcp_yuandian_open_platform_yuandian_search_companies` / `mcp_yuandian_open_platform_yuandian_search_company_profiles_by_name`
   - 企业工商详情（法定代表人、住所地、股东等）：`mcp_yuandian_open_platform_yuandian_get_company_basic_profile` / `mcp_yuandian_open_platform_yuandian_get_company_profile`
   - 涉诉与执行排查：`yuandian_list_company_litigation_document_summaries`（涉诉文书）、`yuandian_list_company_judicial_enforcement_records`（被执行人）、`yuandian_list_company_judgment_defaulter_records`（失信被执行人）。
2. **查法条（原文核对与效力验证）**：
   - 法条关键词/条号精准检索：`mcp_yuandian_open_platform_yuandian_search_legal_articles`
   - 法律法规自然语言语义检索：`mcp_yuandian_open_platform_yuandian_semantic_search_legal_articles`
   - 法条/法规正文详情查询：`mcp_yuandian_open_platform_yuandian_get_legal_article_detail` / `mcp_yuandian_open_platform_yuandian_get_law_or_regulation_detail`
   - 法律引用时效与原文核验：优先调用 `mcp_yuandian_open_platform_yuandian_get_legal_article_detail` 核对现行有效条文（注：`hall_detect` 接口需 VIP 权限，日常无需调用）。
3. **查案例（权威案例与类案检索——绝对红线）**：
   - 权威/指导/典型案例检索：`mcp_yuandian_open_platform_yuandian_search_authoritative_cases`
   - 普通裁判文书检索：`mcp_yuandian_open_platform_yuandian_search_judicial_cases`
   - 案例语义相似度检索：`mcp_yuandian_open_platform_yuandian_semantic_search_cases`
   - 案例详情提取：`mcp_yuandian_open_platform_yuandian_get_case_detail`
   - **案例来源唯一性与禁搜外网**：真实司法案例只能以元典 MCP 为唯一检索源，严禁使用任何通用联网搜索引擎（如 web_search）查询案例交付用户，严防营销号与自媒体虚假拼接或篡改案例入库信息。
   - **案号与入库编号准确核实**：引用元典案例必须标明公网（如中国裁判文书网、人民法院案例库官网）可查的真实准确裁判案号，或人民法院案例库官方入库编号（形如 `2024-xx-x-xxx-xxx`），严禁仅交付需 VIP 或登录鉴权的第三方私网链接。
   - **严格区分层级与零编造**：严禁混淆“人民法院案例库”（固定入库编号）、“最高人民法院指导性案例”（固定称谓“指导案例XX号”）、“最高人民法院公报案例”（载《最高人民法院公报》）与普通典型/解纷案例。元典权威案例库（`authoritative_case_sources`）未收录时，必须如实陈述“经权威库核实暂未收录”，严禁虚构入库标识，严禁强行拼凑。
4. **法规核验定向辅助（仅限法条原文，不适用于案例）**：
   - 当元典库未收录最新地方规范或需核验现行最新条文时，可辅以定向检索国家法律法规数据库（flk.npc.gov.cn）或最高人民法院官网（court.gov.cn）核对法条原文。

## 二、法条引用与核验规范

1. **精准匹配与法名条号规范**：
   - 单争点单法条原则：起草文书时，每个争议焦点仅选用一条最核心、最直接对应的法律条文，不堆砌无争议的合同定义或基础原则通则法条。
   - 引用法律、行政法规、司法解释时，使用完整的官方名称并加书名号（如《中华人民共和国民法典》），条文序号统一规范为中文数字格式（如“第五百七十七条”）。

2. **元典权威原文逐字核验**：
   - 凡在文书中引用法条原文，必须调用元典 MCP 法条详情接口（`mcp__yuandian_open_platform__yuandian_get_legal_article_detail`，传入 `regulation_name` 与 `article_number`）获取现行有效官方条文正文，逐字比对文字、虚词与标点符号，确保无一字偏差。
   - 当元典库未收录特殊地方规范时，调用系统内置 `web_search` 定向检索国家法律法规数据库（flk.npc.gov.cn）或最高人民法院官网（court.gov.cn）核对原文，不凭模型记忆默写。

3. **原文引述一致性**：
   - 审查文书时，仅将法律法规、司法解释作为法条核查；但在起草或审查文书中引用合同条款、协议约定或裁判文书认定时，同样应当使用冒号加双引号（：“……”）一字不差照录原件内容，不得缩写或篡改。
