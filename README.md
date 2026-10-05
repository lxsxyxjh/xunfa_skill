# 寻法法律技能

为 WorkBuddy、Hermes、OpenClaw 等支持 Skill 的 AI 工具提供文件解析、法条检索、文书起草和法律文书 DOCX 导出。

[完整使用教程](https://www.kdocs.cn/l/cuYuk25bp64y)

## 安装与登录

把下面这段话发给你的 AI 工具：

```text
使用 Git 克隆方式安装 Skill：https://gitee.com/buyixjh/xunfa_skill
读取技能，介绍用法，并引导我完成微信扫码登录。
```

扫码后通常会自动确认登录；如果没有继续，可以告诉它“我已登录”。

## 使用

直接描述需求，例如“读取这个 PDF”“核验文中的法条”“起草一份答辩状并导出 DOCX”。支持手动调用的工具，也可以先输入 `/xunfa-legal-workflow` 再描述任务。

## PDF 与图片识别

建议配置自己的百度 OCR 密钥。在[百度智能云控制台](https://console.bce.baidu.com/ai-engine/ocr/overview/index)完成实名认证、创建应用，取得 API Key 和 Secret Key 后，按工具引导配置；也可以登录[寻法账户中心](https://xunfakeji.com/page/userInfo)填写。

## 更新

告诉 AI 工具：“检查并更新已安装的寻法 Skill，保留本地修改。”

本项目需要 Python 3.9 或以上，无需安装第三方 Python 依赖。开发入口为 `scripts/xunfa.py`，具体流程见 `SKILL.md` 和 `references/`。
