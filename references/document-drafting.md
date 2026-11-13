# 法律文书起草规范

起草起诉状、答辩状、上诉状、民事判决书、行政复议申请书、行政复议答辩书、强制执行申请书、财产保全申请书、代理意见、质证意见、开庭提纲、证据目录或其他完整法律文书时使用本规范。

## 一、起草通用规则与正向引导

1. **诉讼请求全面性与当事人信息规范**：
   - 起诉状与申请书：起草前全面检索案涉合同中的付款节点与违约责任条款。凡合同明确约定由违约方承担的维权支出（如律师服务费/律师费、诉讼费、保全费、保全担保保险费、评估鉴定费等），必须全量提炼为诉讼请求项，保障委托人合法权益完整主张。
   - 答辩状/答辩书禁止设立“答辩请求”：答辩人是被动应诉方，无独立请求权，严禁设立“答辩请求”模块；答辩文书在当事人信息后直接切入事实与理由，在文末提出依法驳回原告诉讼请求或维持原行政行为的答辩意见。
   - 当事人信息与法定代表分行呈现：
     - 自然人标准格式（单行横排）：`[诉讼地位]：[姓名]，[性别]，[出生年月日]出生，[民族]，公民身份号码：[身份证号]，住[住址]，联系电话：[电话]。`
     - 法人/行政机关标准格式（两行呈现）：
       `[诉讼地位]：[名称]，住所地：[住所地]，统一社会信用代码：[代码]。`
       `法定代表人：[姓名]，[职务]。`
   - 答辩文书称谓规范：抬头列明法定诉讼地位，如`答辩人（被告）：`对应`被答辩人（原告）：`，行政复议为`答辩人：`对应`被答辩人（申请人）：`；正文事实与理由论述中，统一直接称呼为“原告”或“申请人”，严禁使用“被答辩人”。
   - 涉及企业、村民委员会等组织主体时，起草前优先调用元典 MCP（`yuandian_search_company_pr_095ad592`）检索补全准确的统一社会信用代码、法定代表人及注册/登记住所地。对材料及公开检索中均未载明的非核心字段（如被告缺失的联系电话），直接省略该字段，无需填写“待补充”占位符。
   - 模拟/示例起草身份规则：用户要求示例起草或虚拟生成文书时，自然人公民身份号码必须严格符合 GB 11643-1999 校验位算法，且第 7-14 位出生日期、第 17 位性别码必须与当事人文本信息保持完全一致，以确保 `xunfa.py prepare` 校验通过。
   - 联系方式：统一使用“联系电话：”，支持 11 位手机号码及带区号的标准固定电话（如 `0662-6500899`）；自然人身份证件统一使用“公民身份号码：”并通过校验算法核验。
   - 论述标题规范：各论述大段的标题（如“一、……”）支持采用观点鲜明、直接提炼争议焦点的完整长句，论述标题末尾统一不加任何标点符号。
   - 落款规范：具状人、代理人、答辩人、上诉人、申请人等落款冒号后严格留空（如“具状人：”、“答辩人：”），禁止自行填入当事人名称或“（印章）”字样，日期统一保留空白手签格式（“  年   月   日”）；判决书审判员及书记员署真实/虚拟姓名，日期采用中文数字（如“二〇二六年四月八日”）。

2. **客观事实切入与原文精确照录**：
   - 正文首句直接从具体的时间、主体、案涉客观事实或履约行为切入，按时间脉络自然陈述；民事、行政文书统一使用“案涉”，刑事文书使用“涉案”。
   - 引用合同条款、协议约定、函件或裁判文书认定时，必须使用冒号加双引号（：“……”）一字不差照录原文（冒号前不留空格，引号后仍有接续论述的加逗号“……”，），不作意译概括或删减篡改，确保引述与证据原件完全一致。

3. **单争点核心法条与单段紧凑三段论**：
   - 单争点单核心法条：每个争议焦点仅提炼一条最贴切、最具有针对性的核心法条，避免堆砌无争议的基础原则法条或合同定义法条（如无争议的合同定义、一般履行原则等）。
   - 权威原文核验：引用的每一条法条必须通过元典 MCP 法条详情接口（`yuandian_get_legal_article_detail`）逐字核验现行有效官方原文，确保字句、标点与权威数据库完全一致。
   - 单段连贯三段论：每个小标题下的论述按照“陈述客观事实 —— 引用核心法条原文 —— 得出具体结论”在同一个自然段内紧凑连贯完成，法条引用紧接在事实陈述之后，法条前不独立换行。
   - 标点与段落：功能大标题（如“诉讼请求：”、“事实与理由：”）尾部加冒号；论述小标题（如“一、标题内容”）末尾不加标点；诉讼请求等列表项统一用句号结尾，不使用分号；全文单次回车分段，无多余空行。

4. **反“AI味”精炼准则**：
   - 禁用伪专业套话与互联网黑话：`进一步印证`、`切断`、`证据链`、`完整证据链`、`形成完整证据链`、`至关重要`、`彻底落空`、`闭环`、`资金闭环证据`、`逻辑闭环`、`印证闭环`、`一揽子`、`焊死`、`锁定事实`、`铁证如山`（`xunfa.py prepare` 引擎会自动扫描拦截上述词汇）；
   - 不使用“结论性引导句+冒号”后展开事实的总分结构（如“双方合意真实有效：原告于……”）；
   - 不使用主观绝对化断言与情绪化修辞；
   - “综上所述”仅在文书最终结尾段使用一次。

5. **法律文书本地规则预检与 Word 默认导出（强约束）**：
   - 起草好文书纯文本并保存为临时 txt 后，先调用本地校验引擎自检：`python scripts/xunfa.py prepare --text-file "<临时txt路径>" --output "<新路径_ctx.json>"`，确认 `itemErrors: 0` 且 `ruleIssues: 0`。
   - 校验通过后，调用 `python scripts/xunfa.py docx --input "<临时txt路径>" --output "<输出路径>.docx"` 导出标准排版 Word 文档。成品单一落点：落在 agent 宿主工作区根目录（触发客户端文件卡片），回复中给出绝对路径。

## 二、固定文书模板

### 1. 民事起诉状
民事起诉状
原告：[姓名]，[性别]，[出生年月日]出生，[民族]，公民身份号码：[身份证号]，住[住址]，联系电话：[电话]。
被告：[名称]，住所地：[住所地]，统一社会信用代码：[代码]。
法定代表人：[姓名]，[职务]。
案由：[案由]
诉讼请求：
一、[主张支付本金及利息违约金]。
二、[主张合同明确约定的律师服务费、保全费、保全保险费等实际损失]。
三、[法定优先受偿权或其他诉求]。
四、判令被告承担本案诉讼费用。
事实与理由：
[原告因与被告……一案，依法提起诉讼。]
一、[第一个大段的争点长句或标题（尾部无标点）]
[客观履约事实陈述。引用核心法律条文：“……”，得出该争点论述结论。]
二、[第二个大段的争点长句或标题（尾部无标点）]
[违约事实与维权损失陈述。引用核心法律条文：“……”，得出该争点论述结论。]
综上所述，[总结全文核心观点]
此致
[受诉人民法院名称]
具状人：
  年   月   日

### 2. 民事答辩状
民事答辩状
答辩人（被告）：[姓名/名称]，[性别/住所地]，[出生年月日出生/统一社会信用代码：代码]……
法定代表人：[姓名]，[职务]。（答辩人为法人时列明）
被答辩人（原告）：[姓名/名称]，[性别/住所地]，[出生年月日出生/统一社会信用代码：代码]……
法定代表人：[姓名]，[职务]。（被答辩人为法人时列明）
答辩人就原告[原告姓名/名称]诉被告[被告姓名/名称][案由]一案，案号为[案号]，依法提出如下答辩意见。（注：正文事实与理由论述中统一称“原告”，不使用“被答辩人”）
事实与理由：
一、[第一个大段的争点长句或标题（尾部无标点）]
[事实-法律-结论单段连贯论述]
二、[第二个大段的争点长句或标题（尾部无标点）]
[事实-法律-结论单段连贯论述]
综上所述，原告的诉讼请求缺乏事实与法律依据，请求依法驳回原告的诉讼请求。
此致
[人民法院名称]
答辩人：
  年   月   日

### 3. 民事上诉状
民事上诉状
上诉人（原审被告/原告）：[姓名]，[性别]，[出生年月日]出生，[民族]，公民身份号码：[身份证号]，住[住址]，联系电话：[电话]。
被上诉人（原审原告/被告）：[姓名]，[性别]，[出生年月日]出生，[民族]，公民身份号码：[身份证号]，住[住址]，联系电话：[电话]。
上诉请求：
一、撤销[原审法院名称][原审案号]民事判决第[X]项。
二、改判驳回被上诉人的诉讼请求（或改判支持上诉人一审的诉讼请求）。
三、判令被上诉人承担本案一审、二审诉讼费用。
事实与理由：
上诉人[姓名]因与被上诉人[姓名][案由]一案，不服[原审法院名称][原审案号]民事判决，依法提起上诉。
一、[第一个大段的争点长句或标题（尾部无标点）]
[事实-法律-结论单段连贯论述]
二、[第二个大段的争点长句或标题（尾部无标点）]
[事实-法律-结论单段连贯论述]
综上所述，[总结全文核心观点]
此致
[二审人民法院名称]
上诉人：
  年   月   日

### 4. 代理意见
代理意见
审判长、审判员：
我作为[委托人姓名]的代理人，就[委托人姓名]诉[对方当事人名称][案由]一案，案号[案号]，发表以下意见。
一、[第一个大段的争点长句或标题（尾部无标点）]
[事实-法律-结论单段连贯论述]
二、[第二个大段的争点长句或标题（尾部无标点）]
[事实-法律-结论单段连贯论述]
综上所述，[总结全文核心观点]
此致
[人民法院名称]
代理人：
  年   月   日

### 5. 行政复议申请书
行政复议申请书
申请人：[姓名]，[性别]，[民族]，[出生日期]出生，公民身份号码：[身份证号]，住[住址]，联系电话：[电话]。
被申请人：[机关名称]，住所地：[住所地]，统一社会信用代码：[代码]。
法定代表人：[姓名]，[职务]。
复议请求：
一、[具体复议请求内容]
事实与理由：
一、[第一个大段的争点长句或标题（尾部无标点）]
[事实-法律-结论单段连贯论述]
二、[第二个大段的争点长句或标题（尾部无标点）]
[事实-法律-结论单段连贯论述]
综上所述，[总结全文核心观点]
此致
[复议机关名称]
申请人：
  年   月   日

### 6. 行政复议答辩书
行政复议答辩书
答辩人：[机关名称]，住所地：[住所地]，统一社会信用代码：[代码]。
法定代表人：[姓名]，[职务]。
被答辩人（申请人）：[姓名]，[性别]，[民族]，[出生日期]出生，公民身份号码：[身份证号]，住[住址]，联系电话：[电话]。
答辩人因申请人[姓名]不服答辩人于[日期]作出的[具体行政行为名称/决定书文号]申请行政复议一案，依法提出答辩如下。（注：正文事实与理由论述中统一称“申请人”，不使用“被答辩人”）
事实与理由：
一、[第一个大段的争点长句或标题（尾部无标点）]
[客观事实陈述。引用核心法律条文：“……”，得出该争点论述结论。]
二、[第二个大段的争点长句或标题（尾部无标点）]
[法定职责与程序合法性陈述。引用核心法律条文：“……”，得出该争点论述结论。]
综上所述，答辩人作出的案涉行政行为认定事实清楚，证据确凿，适用依据正确，程序合法，内容适当。请求依法驳回申请人的行政复议请求，维持答辩人作出的行政行为。
此致
[行政复议机关名称]
答辩人：
  年   月   日

### 7. 质证意见
质证意见（[原告/被告姓名]提交）
一、证据[序号]《[证据名称1]》
[能不认可的尽量不认可，如：真实性、合法性、关联性、证明目的均不认可。必须认可、对我方有利的，才可以认可某些性质]
[切入事实矛盾或形式瑕疵，不必须引用法条，不必须做三段论展开，直接论述为何不予认可]。上述证据无法证明[对方拟达到的证明目的]。
二、证据[序号]《[证据名称2]》、证据[序号]《[证据名称3]》
真实性、合法性、关联性予以认可，证明目的不认可。
[结合矛盾客观事实进行简要论述]。
提交人：
  年   月   日

### 8. 开庭提纲
开庭提纲
一、时间节点
1. [时间节点一：日期及对应事项简述]
2. [时间节点二：日期及对应事项简述]
3. [时间节点三：日期及对应事项简述]
二、相关事实（双方无争议或一方自认的事实）
1. [事实陈述一]
2. [事实陈述二]
3. [事实陈述三]
三、争议焦点
1. [争议焦点一]
2. [争议焦点二]
3. [争议焦点三（如有）]
四、法律依据
1. [法规名称及条文号]：“[条文原文]”
2. [法规名称及条文号]：“[条文原文]”
五、注意要点（可选）
1. [庭审提问要点或突发情况预案]
2. [妥协底线或调解方案]

### 9. 证据目录专项规则与表格版生成规范

#### （1）实体内容与实务逻辑规则
1. **证据取舍边界**：
   - 严禁列入纯诉讼程序材料：原告身份证复印件、律所内部手续（委托合同、授权委托书、谈话笔录、保证书）仅属于立案和代理权限审查材料，绝对不列入证据目录；
   - 被告主体证明入列：被告企业信用信息公示系统查询信息（或被告身份证复印件）可列入证据目录序号1，证明被告合法的民事诉讼主体资格；
   - 坚决剔除无关材料：与案涉待证事实无实质关联或无证明效力的材料一律剔除，避免证据冗余与无效举证。
2. **缺件占位红线（缺证只能占位，严禁自制伪造）**：
   - 缺件判定：组卷前对证据目录逐项盘点原始材料，凡案卷或用户资料中不存在用户提供的对应原始材料的证据项一律判定为缺件；
   - 缺件三禁：严禁调用元典 MCP 或联网检索数据自制企业信息表格充当证据页（检索数据只能用于起诉状等文书正文当事人信息栏补全，不是证据）；严禁手写模拟企业信用信息公示系统样式、红章、防伪视觉；严禁拿其他案件类似材料顶替；
   - 占位页版式：A4 竖屏（595.27 × 841.89 pt）纯空白页，页面居中仅写一行“此页应当为：[证据项名称]”，仿宋加粗小二号（18pt），不加括号补充说明、不加灰字备注、不加水印、不加任何装饰；
   - 页码与回填闭环：占位页照常列入证据目录并纳入总册连续页码编号，页码列回填占位页实际物理页码，用户补充原始材料后原位替换该页重新组卷；
   - 交付汇报：必须在回复中逐项列出缺件清单，明确哪些证据项当前为占位页、各需补充什么材料。
3. **证据项合并与顺序编排（紧扣起诉状顺序）**：
   - 编排顺序与起诉状事实发生时序严格一致（主体资格 -> 合同关系 -> 实际身份 -> 出险事故 -> 就诊因果 -> 评残及判决认定）；
   - **关联证据合并连接词**：多份紧密关联证据合并在同一项时，名称之间严禁使用“及”连接，一律使用中文顿号“、”连接（例如：《司法鉴定意见书》、民事判决书）；
   - **证明内容原文映射（核心原则）**：证明目的严禁脱离起诉状天马行空，最好直接原文照搬起诉状对应的事实语句，做到“起诉状说一句，证据目录证一句”，在庭审举证时形成一对一的精确投射；
   - **括号极简化控制（核心铁律）**：除案件原生自带信息（如案号、鉴定文号、法定诉讼地位）外，证据名称与证明目的中严禁随手添加括号（如保单号、车架号、代码、负责人姓名、停放场景等一律用逗号或文字自然连接），确保全篇干净严谨。

#### （2）标准 Word 表格版式与排版强规范
1. **页面与字体字号规范**：
   - 版面边距：标准 A4 页面，上边距 2.54 cm，下边距 2.54 cm，左边距 2.80 cm，右边距 2.80 cm；
   - 大标题排版：居中放置于表格正上方（独立段落，不放在表格内部），字体统一为“仿宋小二号（18pt）”，加粗，保留段后 12pt 间距；
   - 表格与正文字体：全表表头、正文、序号、页码严格统一为“仿宋4号字体（14pt）”；
   - 全篇文字无缩进：表格内部所有文字彻底取消首行缩进（首行缩进=0，左缩进=0）。
2. **表格各列对齐与列宽分配（标准 4 列表格，版心总宽约 15.6 cm）**：
   - 第1列【序号】：列宽 1.5 cm，水平居中（CENTER），垂直居中（CENTER）；
   - 第2列【证据名称】：列宽 4.0 cm，水平居左（LEFT），垂直居中（CENTER）；
   - 第3列【证明目的】：列宽 8.5 cm，两端对齐（JUSTIFY），垂直居中（CENTER），多条证明目的按“1、”“2、”分行紧凑排列；
   - 第4列【页码】：列宽 1.6 cm，水平居中（CENTER），垂直居中（CENTER）。
3. **第二页跨页表头自动重复（消除大标题重复）**：
   - 由于大标题位于表格正上方独立段落，表格第0行即为列标题表头【序号 | 证据名称 | 证明目的 | 页码】；
   - 在表格第0行（header_row）的 trPr 中注入 `<w:tblHeader/>` 与 `<w:cantSplit/>`；跨页延伸至第二页时，自动仅在第二页顶端重复列标题表头，第二页绝不重复大标题。
4. **动态页码规范（仿宋4号字 1/2 格式）**：
   - 页脚居中，格式严格为“当前页/总页数”（如 1/2）；
   - 通过底层 XML 域代码，将页码中的三个字符（PAGE 域字符、斜杠“/”、NUMPAGES 域字符）外层及每个 Run 节点全部显式注入仿宋 4 号属性（sz=28），杜绝任何软件降级。

#### （3）Python 自动化构建 Word（docx）代码模板
```python
import docx
from docx.shared import Pt, Cm
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

def generate_evidence_docx(out_path, title_text, headers, evidence_data):
    doc = docx.Document()
    section = doc.sections[0]
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(2.8)
    section.right_margin = Cm(2.8)

    # 1. 注入规范页脚 (仿宋4号，1/2 三字符完全锁定)
    footer = section.footer
    footer.is_linked_to_previous = False
    old_p = footer.paragraphs[0]
    old_p._p.getparent().remove(old_p._p)

    footer_xml = r'''
    <w:p %s>
      <w:pPr>
        <w:pStyle w:val="Footer"/>
        <w:jc w:val="center"/>
        <w:rPr>
          <w:rFonts w:ascii="仿宋" w:eastAsia="仿宋" w:hAnsi="仿宋" w:cs="仿宋"/>
          <w:sz w:val="28"/><w:szCs w:val="28"/>
        </w:rPr>
      </w:pPr>
      <w:r><w:rPr><w:rFonts w:ascii="仿宋" w:eastAsia="仿宋" w:hAnsi="仿宋" w:cs="仿宋"/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr><w:fldChar w:fldCharType="begin"/></w:r>
      <w:r><w:rPr><w:rFonts w:ascii="仿宋" w:eastAsia="仿宋" w:hAnsi="仿宋" w:cs="仿宋"/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>
      <w:r><w:rPr><w:rFonts w:ascii="仿宋" w:eastAsia="仿宋" w:hAnsi="仿宋" w:cs="仿宋"/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr><w:fldChar w:fldCharType="separate"/></w:r>
      <w:r><w:rPr><w:rFonts w:ascii="仿宋" w:eastAsia="仿宋" w:hAnsi="仿宋" w:cs="仿宋"/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr><w:t>1</w:t></w:r>
      <w:r><w:rPr><w:rFonts w:ascii="仿宋" w:eastAsia="仿宋" w:hAnsi="仿宋" w:cs="仿宋"/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr><w:fldChar w:fldCharType="end"/></w:r>
      <w:r><w:rPr><w:rFonts w:ascii="仿宋" w:eastAsia="仿宋" w:hAnsi="仿宋" w:cs="仿宋"/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr><w:t>/</w:t></w:r>
      <w:r><w:rPr><w:rFonts w:ascii="仿宋" w:eastAsia="仿宋" w:hAnsi="仿宋" w:cs="仿宋"/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr><w:fldChar w:fldCharType="begin"/></w:r>
      <w:r><w:rPr><w:rFonts w:ascii="仿宋" w:eastAsia="仿宋" w:hAnsi="仿宋" w:cs="仿宋"/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr><w:instrText xml:space="preserve"> NUMPAGES </w:instrText></w:r>
      <w:r><w:rPr><w:rFonts w:ascii="仿宋" w:eastAsia="仿宋" w:hAnsi="仿宋" w:cs="仿宋"/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr><w:fldChar w:fldCharType="separate"/></w:r>
      <w:r><w:rPr><w:rFonts w:ascii="仿宋" w:eastAsia="仿宋" w:hAnsi="仿宋" w:cs="仿宋"/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr><w:t>1</w:t></w:r>
      <w:r><w:rPr><w:rFonts w:ascii="仿宋" w:eastAsia="仿宋" w:hAnsi="仿宋" w:cs="仿宋"/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr><w:fldChar w:fldCharType="end"/></w:r>
    </w:p>
    ''' % nsdecls('w')
    footer._element.append(parse_xml(footer_xml))

    # 2. 独立大标题：仿宋小二 (18pt)，加粗居中，段后 12pt
    title_p = doc.add_paragraph()
    title_p.alignment = docx.enum.text.WD_PARAGRAPH_ALIGNMENT.CENTER
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(12)
    r_t = title_p.add_run(title_text)
    r_t.font.name = '仿宋'
    r_t._r.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), '仿宋')
    r_t.font.size = Pt(18)
    r_t.font.bold = True

    # 3. 创建 4 列表格
    table = doc.add_table(rows=1, cols=4)
    table.alignment = docx.enum.table.WD_TABLE_ALIGNMENT.CENTER

    tblPr = table._tbl.tblPr
    tblPr.append(parse_xml(r'''
        <w:tblBorders %s>
            <w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>
            <w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>
            <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>
            <w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>
            <w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        </w:tblBorders>
    ''' % nsdecls('w')))
    tblPr.append(parse_xml(r'''
        <w:tblCellMar %s>
            <w:top w:w="120" w:type="dxa"/><w:left w:w="160" w:type="dxa"/>
            <w:bottom w:w="120" w:type="dxa"/><w:right w:w="160" w:type="dxa"/>
        </w:tblCellMar>
    ''' % nsdecls('w')))

    col_widths = [Cm(1.5), Cm(4.0), Cm(8.5), Cm(1.6)]

    # 4. 表头配置：注入 tblHeader 实现跨页重复表头，注入 cantSplit 防止截断
    h_row = table.rows[0]
    h_row._tr.get_or_add_trPr().append(parse_xml(r'<w:tblHeader %s/>' % nsdecls('w')))
    h_row._tr.get_or_add_trPr().append(parse_xml(r'<w:cantSplit %s/>' % nsdecls('w')))

    for i, h in enumerate(headers):
        cell = h_row.cells[i]
        cell.width = col_widths[i]
        cell._tc.get_or_add_tcPr().append(parse_xml(r'<w:vAlign %s w:val="center"/>' % nsdecls('w')))
        p = cell.paragraphs[0]
        p.alignment = docx.enum.text.WD_PARAGRAPH_ALIGNMENT.CENTER
        p.paragraph_format.first_line_indent = Pt(0)
        p.paragraph_format.left_indent = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(h)
        run.font.name = '仿宋'
        run._r.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), '仿宋')
        run.font.size = Pt(14)
        run.font.bold = True

    # 5. 循环填充数据行
    for item in evidence_data:
        row = table.add_row()
        row._tr.get_or_add_trPr().append(parse_xml(r'<w:cantSplit %s/>' % nsdecls('w')))

        alignments = [
            docx.enum.text.WD_PARAGRAPH_ALIGNMENT.CENTER,   # 序号居中
            docx.enum.text.WD_PARAGRAPH_ALIGNMENT.LEFT,     # 名称居左
            docx.enum.text.WD_PARAGRAPH_ALIGNMENT.JUSTIFY,  # 目的两端对齐
            docx.enum.text.WD_PARAGRAPH_ALIGNMENT.CENTER    # 页码居中
        ]

        vals = [item['num'], item['name'], item['goals'], item['page']]
        for c_idx in range(4):
            cell = row.cells[c_idx]
            cell.width = col_widths[c_idx]
            cell._tc.get_or_add_tcPr().append(parse_xml(r'<w:vAlign %s w:val="center"/>' % nsdecls('w')))

            val = vals[c_idx]
            paragraphs = val if isinstance(val, list) else [val]
            for p_idx, text in enumerate(paragraphs):
                p = cell.paragraphs[0] if p_idx == 0 else cell.add_paragraph()
                p.alignment = alignments[c_idx]
                p.paragraph_format.first_line_indent = Pt(0)
                p.paragraph_format.left_indent = Pt(0)
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.15
                run = p.add_run(text)
                run.font.name = '仿宋'
                run._r.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), '仿宋')
                run.font.size = Pt(14)

    doc.save(out_path)
```

#### （4）诉讼证据材料组卷、图片转PDF、全本合并与连续页码加注规程（方案A实战标准）
1. **证据原件/全本提交红线与后附法条清理**：
   - 判决书、裁定书、司法鉴定意见书等法定裁决与证明文书在组卷时必须提交全文，绝对严禁提取“首尾页及事实认定页”或局部截取，必须保障文书完整生效力与既判力证据形式；
   - **后附法条清理红线**：判决书末尾所附的“相关法律条文/附相关法条”不属于裁判正文，组卷时必须彻底剔除（仅提取保留至审判人员、助理及书记员落款页止），避免污染证据页数与造成无效冗余。
2. **图片材料A4规范化与智能横竖屏识别标准（绝不剪切）**：
   - 读取凭证图片分辨率 (W, H)，当宽/高 >= 1.15（宽明显大于高，如全国企业信用信息公示系统截图）时，自动判定为横版材料，自适应生成标准 A4 横屏 PDF（宽 841.89 pt × 高 595.27 pt），预留四周 8mm 极小边距等比居中铺满，绝不剪切原图任何像素，高保真还原全国统一系统防伪视觉；
   - 当高 >= 宽时生成标准 A4 竖屏 PDF（595.27 × 841.89 pt）。横版页面页码自适应放置在横屏右下角。
3. **缺件占位页生成规程（缺证只能占位，严禁自制伪造）**：
   - 组卷前逐项核对证据目录与案卷原始材料，缺件项一律生成占位页并保持证据目录照常列项，严禁自制企业信息表格、模拟公示系统截图或其他任何替代伪造页；
   - 占位页用 pymupdf 新建 A4 竖屏页，居中单行“此页应当为：[证据项名称]”，仿宋加粗小二号（18pt），干净空白、无括号补充、无灰字备注、无水印装饰；
   - 占位页按其所属证据项的自然层级点号前缀命名（如证据1缺件则单项 PDF 命名为 `1_占位_被告主体信息.pdf`），与其他单项证据同样顺序合并入总册并统一加注连续页码，页码反向回填时按实际物理页码计入；
   - 中文字体嵌入铁律：占位页中文必须走 pymupdf 真实字体文件嵌入（TextWriter + Font），严禁套用纯数字页码的 WinAnsi 单字节 TrueType 手写方案绘制中文（该方案仅适用于阿拉伯数字页码，双字节中文传入单字节编码会错位乱码）。完整代码模板见本节末尾。
4. **自然层级点号命名与双案独立目录**：
   - 涉多个独立相对方/合同的诉讼案件，必须分别建立独立的案卷子目录（如 `1、原告诉被告A`、`2、原告诉被告B`），各自独立成套存放起诉状、回填物理页码的证据目录及合并证据册；
   - 在各案卷工作目录下，各单项材料转换为独立 PDF 并采用 `1_`、`2.1_`、`2.2_` 自然层级点号前缀命名，确保在文件管理器中按自然顺序绝对对齐；
   - 按照证据目录顺序，将各单项 PDF 顺序合并为一个总册《证据材料.pdf》，严禁交付任何“无页码原版”等未完成半成品，必须交付唯一成品。
5. **动态连续页码加注（WPS原生可编辑架构与编码防乱码规程）**：
   - 提取总合并页数 N；
   - 逐页自适应获取页面宽高（`page.mediabox.width` / `height`），在每页右下角（距最右 1.0cm 即 28.35pt、距底边 1.36cm 即 38.69pt）绘制纯阿拉伯数字（`1`、`2`、`3`……）；
   - 字体严格采用仿宋小二号（18pt），无边框、无背景底色，干净整齐。
   - **底层字符编码铁律（根除乱码死穴）**：页码纯阿拉伯数字属于单字节字符，其字体字典必须采用标准单字节编码（`/Encoding /WinAnsiEncoding`，子类型为 `/Subtype /TrueType`，基础字体 `/BaseFont /SimSun` 或 `/FangSong`，且包含完整的 ASCII `/Widths` 数组与 `/FontDescriptor` 描述符）。绝对严禁手写未嵌入 `/ToUnicode` 映射表的双字节复合字体（如 `/Subtype /Type0` + `/Encoding /UniGB-UCS2-H`）来绘制单字节 ASCII 字符串 `[(1)] TJ`，否则在 WPS/Acrobat 中会强行双字节错位查表解码，错位命中汉字库中的生僻偏旁部首（形似左右反转的 F）或汉字“(特)”！
   - **WPS 原生可编辑架构注入（彻底支持客户端增删改）**：在每一页内容流末尾注入 `/Artifact <</Contents(页码)/Subtype/Header/Type/Pagination>>BDC ... EMC` 标记，并绑定带有 `/PieceInfo /ADBE_CompoundType`（内含 `<HeaderFooterSettings version="8.0">` XML 流）的 Form XObject。生成的 PDF 在 WPS 客户端中点击【更新页码】或【删除页码】时可原生识别、直接弹窗允许增删改。
   - **对象流引用覆盖 BUG 防范**：先将所有原始页面添加进 writer，严禁先对 reader.pages 盖印再 add_page，否则同一多页文档的后续页面会被底层对象流引用覆盖导致盖印丢失。
6. **真实物理页码反向回填闭环（核心法则）**：
   - 证据材料总册生成完毕后，统计各证据项在总册中的起始与截止物理页码；
   - 将该真实连续物理页码反向回填更新至证据目录 Word 的“页码”列，重新导出交付，彻底消除“目录页码与材料页码不符”的重大诉讼隐患。

```python
import os, io, pypdf
from pypdf.generic import (
    DictionaryObject, NameObject, TextStringObject, NumberObject,
    ArrayObject, DecodedStreamObject
)

def build_wps_native_evidence_pdf(file_paths, out_pdf_path):
    writer = pypdf.PdfWriter()
    
    # 1. 构建标准单字节 TrueType 字体对象 (WinAnsiEncoding 彻底杜绝双字节乱码)
    fd = DictionaryObject()
    fd[NameObject('/Type')] = NameObject('/FontDescriptor')
    fd[NameObject('/FontName')] = NameObject('/SimSun')
    fd[NameObject('/Flags')] = NumberObject(32)
    fd[NameObject('/ItalicAngle')] = NumberObject(0)
    fd[NameObject('/Ascent')] = NumberObject(859)
    fd[NameObject('/Descent')] = NumberObject(-140)
    fd[NameObject('/FontBBox')] = ArrayObject([NumberObject(-7), NumberObject(-140), NumberObject(1000), NumberObject(859)])
    fd[NameObject('/CapHeight')] = NumberObject(683)
    fd[NameObject('/StemV')] = NumberObject(0)
    fd_ref = writer._add_object(fd)
    
    fnt = DictionaryObject()
    fnt[NameObject('/Type')] = NameObject('/Font')
    fnt[NameObject('/Subtype')] = NameObject('/TrueType')
    fnt[NameObject('/BaseFont')] = NameObject('/SimSun')
    fnt[NameObject('/Encoding')] = NameObject('/WinAnsiEncoding')
    fnt[NameObject('/FirstChar')] = NumberObject(32)
    fnt[NameObject('/LastChar')] = NumberObject(255)
    fnt[NameObject('/Widths')] = ArrayObject([NumberObject(500)] * 224)
    fnt[NameObject('/FontDescriptor')] = fd_ref
    font_ref = writer._add_object(fnt)
    
    # 2. 注册 OCG 图层 (Headers/Footers)
    ocg_obj = DictionaryObject()
    ocg_obj[NameObject('/Type')] = NameObject('/OCG')
    ocg_obj[NameObject('/Name')] = TextStringObject('Headers/Footers')
    ocg_obj[NameObject('/Usage')] = DictionaryObject({
        NameObject('/PageElement'): DictionaryObject({
            NameObject('/PageElement'): DictionaryObject({NameObject('/Subtype'): NameObject('/HF')})
        })
    })
    oc_md = DictionaryObject({NameObject('/Type'): NameObject('/OCMD'), NameObject('/OCGs'): writer._add_object(ocg_obj)})
    oc_md_ref = writer._add_object(oc_md)
    
    # 3. 注册 HeaderFooterSettings XML 配置流 (WPS 原生识别核心)
    doc_settings_xml = (
        '<?xml version=\"1.0\" encoding=\"UTF-8\" ?>'
        '<HeaderFooterSettings version = \"8.0\">'
        '<Font name=\"FangSong\" type=\"Type0\" size=\"18\"/>'
        '<Color r=\"0\" g=\"0\" b=\"0\"/>'
        '<Margin top=\"36\" left=\"28.3465\" right=\"28.3465\" bottom=\"56.6929\"/>'
        '<Appearance shrink=\"0\" fixedprint=\"0\"/>'
        '<PageRange end=\"-1\" start=\"-1\" even=\"1\" odd=\"1\" />'
        '<Page offset=\"1\"><PageIndex format=\"1\"/></Page>'
        '<Date><Month format=\"1\" />/<Day format=\"1\" /><Year format=\"0\" /></Date>'
        '<Header><Left></Left><Center></Center><Right></Right></Header>'
        '<Footer><Left></Left><Center></Center><Right><Page offset=\"1\">PageIndex format=\"1\"/></Page></Right></Footer>'
        '</HeaderFooterSettings>'
    )
    doc_settings_stream = DecodedStreamObject()
    doc_settings_stream.set_data(doc_settings_xml.encode('utf-8'))
    doc_settings_ref = writer._add_object(doc_settings_stream)
    
    # 4. 构建 PieceInfo 字典
    adbe_dict = DictionaryObject({
        NameObject('/LastModified'): TextStringObject(\"D:20261108070000--16'00'\"),
        NameObject('/Private'): NameObject('/Header'),
        NameObject('/DocSettings'): doc_settings_ref
    })
    piece_info_dict = DictionaryObject({NameObject('/ADBE_CompoundType'): adbe_dict})
    piece_info_ref = writer._add_object(piece_info_dict)
    
    # 5. Catalog 级别注入 PieceInfo (/WPS_ICV)
    wps_icv = DictionaryObject({
        NameObject('/LastModified'): TextStringObject(\"D:20261108070000--16'00'\"),
        NameObject('/DocICV'): DictionaryObject({
            NameObject('/ICV'): TextStringObject('40830DC16C094BABB5C9A81F7BBE55B2_12'),
            NameObject('/TYPE'): TextStringObject('TEXT')
        })
    })
    writer.root_object[NameObject('/PieceInfo')] = DictionaryObject({NameObject('/WPS_ICV'): writer._add_object(wps_icv)})
    
    # 6. 先将所有原始页面完整加载入 writer (避开对象流缓存覆盖 BUG)
    for fp in file_paths:
        r = pypdf.PdfReader(fp)
        for page in r.pages:
            writer.add_page(page)
            
    total_pages = len(writer.pages)
    
    # 7. 逐页注入 Form XObject 与 /Artifact 内容流标记
    for idx in range(total_pages):
        page = writer.pages[idx]
        w, h = float(page.mediabox.width), float(page.mediabox.height)
        page_str = str(idx + 1)
        text_width = len(page_str) * 9.0
        x = w - 28.3465 - text_width
        y = 38.692913 # 约 1.36cm 与 WPS 保持绝对一致
        
        form_xobj = DecodedStreamObject()
        form_xobj[NameObject('/Type')] = NameObject('/XObject')
        form_xobj[NameObject('/Subtype')] = NameObject('/Form')
        form_xobj[NameObject('/BBox')] = ArrayObject([NumberObject(0), NumberObject(-4.5), NumberObject(text_width), NumberObject(22.5)])
        form_xobj[NameObject('/Matrix')] = ArrayObject([NumberObject(1), NumberObject(0), NumberObject(0), NumberObject(1), NumberObject(0), NumberObject(0)])
        form_xobj[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/KSPF1'): font_ref})})
        form_xobj[NameObject('/OC')] = oc_md_ref
        form_xobj[NameObject('/PieceInfo')] = piece_info_ref
        form_xobj.set_data(f'q\\nBT\\n/KSPF1 18.00 Tf\\n1 0 0 1 0 0  Tm\\n0 0 0 rg\\n[({page_str})] TJ\\nET\\nQ\\n'.encode('latin1'))
        form_ref = writer._add_object(form_xobj)
        
        xobj_name = f'/KSPX{idx + 13}'
        if '/Resources' not in page:
            page[NameObject('/Resources')] = DictionaryObject()
        if '/XObject' not in page['/Resources']:
            page['/Resources'][NameObject('/XObject')] = DictionaryObject()
        page['/Resources']['/XObject'][NameObject(xobj_name)] = form_ref
        
        artifact_cmd = f'\n/Artifact <</Contents({page_str})/Subtype/Header/Type/Pagination>>BDC\nq\n1 0 0 1 {x:.6f} {y:.6f} cm\n{xobj_name} Do\nQ\nEMC\n'
        new_content = page.get_contents().get_data() + artifact_cmd.encode('latin1')
        new_stream = DecodedStreamObject()
        new_stream.set_data(new_content)
        # 必须作为间接对象引用注入，严禁直接赋直接对象字典
        new_stream_ref = writer._add_object(new_stream)
        page[NameObject('/Contents')] = new_stream_ref
        
    with open(out_pdf_path, 'wb') as f_out:
        writer.write(f_out)
```

**缺件占位页生成代码模板（pymupdf 真实中文字体嵌入，严禁套用纯数字页码的 WinAnsi 单字节方案绘制中文）：**

```python
import fitz  # pymupdf

def create_placeholder_pdf(evidence_name: str, out_pdf_path: str) -> None:
    """缺件占位页：A4 竖屏纯空白页，居中单行“此页应当为：[证据项名称]”。

    中文字体必须走真实字体文件嵌入（pymupdf 自动子集嵌入），
    严禁复用纯数字页码的 WinAnsi 单字节 TrueType 手写字体方案。
    """
    doc = fitz.open()
    page = doc.new_page(width=595.27, height=841.89)  # A4 竖屏
    font = fitz.Font(fontfile=r"C:/Windows/Fonts/simfang.ttf")  # 仿宋，Windows 自带
    text = f"此页应当为：{evidence_name}"
    fs = 18  # 小二号，与文书大标题字号一致
    tw = font.text_length(text, fontsize=fs)
    x = (page.rect.width - tw) / 2
    y = page.rect.height / 2 + fs / 2  # 视觉垂直居中
    writer = fitz.TextWriter(page.rect)
    writer.append(fitz.Point(x, y), text, font=font, fontsize=fs)
    writer.write_text(page)
    doc.save(out_pdf_path)
    doc.close()

# 用法：证据项缺件时，以该项自然层级前缀命名占位页，与其他单项证据一起参与合并
# create_placeholder_pdf("全国企业信用信息公示系统中被告XX公司的查询信息", "1_占位_被告主体信息.pdf")
```

### 10. 强制执行申请书
强制执行申请书
申请人：[姓名/名称]，住所地：[住所地]，统一社会信用代码：[代码]。（自然人按自然人标准格式）
法定代表人：[姓名]，[职务]。（法人时列明）
被执行人：[姓名/名称]，住所地：[住所地]，统一社会信用代码：[代码]。（自然人按自然人标准格式）
法定代表人：[姓名]，[职务]。（法人时列明）
执行依据：[生效法律文书名称及案号，如（2026）京0108民初1234号民事判决书/调解书]
申请事项：
一、[强制给付本金、利息、违约金等具体事项]。
二、[强制加倍支付迟延履行期间的债务利息]。
三、判令被执行人承担本案执行费用。
事实与理由：
[陈述原生效法律文书作出情况、履行期限届满、被执行人至今未履行给付义务之客观事实，引用核心法律依据，得出申请强制执行结论。]
此致
[执行人民法院名称]
申请人：
  年   月   日

### 11. 财产保全申请书
财产保全申请书
申请人：[姓名/名称]，住所地：[住所地]，统一社会信用代码：[代码]。（自然人按自然人标准格式）
法定代表人：[姓名]，[职务]。（法人时列明）
被申请人：[姓名/名称]，住所地：[住所地]，统一社会信用代码：[代码]。（自然人按自然人标准格式）
法定代表人：[姓名]，[职务]。（法人时列明）
请求事项：
请求依法在人民币[金额]元范围内，对被申请人名下的银行存款予以冻结，或查封、扣押被申请人名下相应价值的不动产、车辆等其他等值财产。
事实与理由：
[陈述案由及案涉纠纷已起诉或即将起诉情况，陈述防止财产转移隐匿之必要性，写明担保方式（保函/自有财产担保）及承担错误保全赔偿责任之承诺，引用核心法律条文，得出保全结论。]
此致
[人民法院名称]
申请人：
  年   月   日

### 12. 民事判决书
[人民法院名称]
民事判决书
[案号]
原告：[姓名/名称]，……
委托诉讼代理人：[姓名]，[律所名称]律师。
被告：[姓名/名称]，……
原告[姓名/名称]与被告[姓名/名称][案由]一案，本院于[立案日期]立案后，依法适用[普通/简易]程序，于[开庭日期]公开开庭进行了审理。原告[姓名/名称]及其委托诉讼代理人[姓名]、被告[姓名/名称]到庭参加诉讼。本案现已审理终结。
原告[姓名/名称]向本院提出诉讼请求：[诉讼请求项]。事实与理由：[起诉事实与理由概述]。
被告[姓名/名称]辩称：[答辩意见要点]。
当事人围绕诉讼请求依法提交了证据，本院组织当事人进行了证据交换和质证。[当事人无异议证据确认及有争议证据审查认证]。
根据当事人陈述和经审查确认的证据，本院认定事实如下：
[查明事实，包括合同签订、履行交付、验收付款、违约情况及维权费用实际发生情况]。
本院认为，[合同效力及义务履行认定。引用核心法律条文：“……”，结合履约事实判定是否违约及违约金、维权支出是否应予支持或调减]。
综上所述，依照[法条名称及条文号]之规定，判决如下：
一、[第一项给付判决]；
二、[第二项给付判决]；
三、驳回[当事人姓名/名称]的其他诉讼请求。
如果未按本判决指定的期间履行给付金钱义务，应当依照《中华人民共和国民事诉讼法》第二百六十四条规定，加倍支付迟延履行期间的债务利息。
案件受理费[金额]元，由[承担主体]负担；财产保全费[金额]元，由[承担主体]负担。
如不服本判决，可以在判决书送达之日起十五日内，向本院递交上诉状，并按对方当事人或者代表人的人数提出副本，上诉于[上一级人民法院名称]。
审判员　[姓名]
[中文数字日期，如二〇二六年四月八日]
书记员　[姓名]

## 三、非固定模板文书
不在上述固定模板之列的法律文书（如执行申请书、申诉书、保全申请书等），严格按照对应诉讼程序的法定结构组织，严格执行本规范中的三段论论证、标点、用词及落款规范。
