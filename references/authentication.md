# 认证与安全

寻法客户端使用用户目录 `.xunfa/auth.json` 保存当前服务地址的登录态。`scripts/xunfa.py` 负责读取、校验和更新此文件；`loginTime` 仅记录登录时间，业务命令的实际响应决定当前登录态是否可用。

默认服务地址为 `https://xunfakeji.com`。用户明确指定本机开发服务时，命令可传 `--base-url`；客户端只接受正式 HTTPS 服务和本机回环地址。

## 微信扫码登录

在当前任务私有临时目录创建二维码：

```bash
python scripts/xunfa.py auth-qr-start --output "<临时目录>/xunfa-login.png"
```

命令返回 `uuid` 与 `qrPath`。展示 `qrPath` 对应图片，请用户使用微信扫码并选择完整服务。随后执行：

```bash
python scripts/xunfa.py auth-qr-wait --uuid "<uuid>"
```

第二条命令会建立 SSE 登录通知连接，扫码成功后只兑换一次登录 Cookie 并保存登录态，连接短暂中断时会自动重新订阅通知。命令结束后返回登录账户名；二维码或扫码结果异常时如实报告命令结果。

## 账号密码登录

终端可交互输入密码时执行：

```bash
python scripts/xunfa.py auth-password --username "<账号>" --password-prompt
```

客户端在内存中计算登录所需摘要，登录成功后保存登录态。密码不写入文件、输出或命令参数。

## 任务中的认证处理

业务命令返回 `auth_missing` 或 `auth_required` 时，完成上述登录流程，再将原业务命令执行一次。第二次返回的实际结果就是本次任务结果。

客户端的标准输出、错误输出、生成文件和答复均不包含 token、密码或 OCR 密钥。
