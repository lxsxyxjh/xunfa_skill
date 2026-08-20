# 认证与安全

## 服务地址与响应

默认服务地址是 `https://fabaotu.com`。只有用户明确指定本机开发环境时，才使用 `FABAO_BASE_URL` 覆盖；仅允许 `localhost`、`127.0.0.1` 或 `::1`，其他远程主机和正式服务的明文 HTTP 会被拒绝。

除文书生成接口外，业务响应统一为：

```json
{"code":"...","msg":"...","data":null}
```

只有 `code=="1"` 表示成功，其他值均为失败，原因读取 `msg`。

## 获取 token

业务接口需要登录态，请求可以使用 Cookie `fabao=<token>` 或请求头 `token=<token>`。依次从以下位置读取 token：

1. 环境变量 `FABAO_TOKEN`；默认只用于正式服务。本机开发 token 必须同时用 `FABAO_TOKEN_BASE_URL` 绑定到同一个回环地址。
2. 用户目录 `.fabao/auth.json` 的 `token` 字段。

`auth.json` 中的 `baseUrl` 必须与本次请求的协议、主机和端口一致，脚本才会发送其中的 token，防止切换服务地址时把登录态带到其他主机。确需使用其他环境时，用户同时明确设置该环境自己的 `FABAO_TOKEN`。

必须使用 JSON 解析器读取 `auth.json`，并严格按以下状态机处理认证：

1. 有 token 且尚未发起业务请求：选择 Cookie 或请求头中的一种方式，直接执行原业务请求，不预先校验登录态，也不同时发送两种凭据。
2. 没有 token：直接执行登录，不发送无凭据的试探请求。
3. 原业务请求返回 `code!="1"` 且 `msg` 包含“请先登录”或“请重新登录”：立即认定当前 token 失效并执行登录。禁止更换 Cookie 或请求头重复发送原 token，禁止再调用其他接口确认 token 是否失效。
4. 登录成功：保存新 token，只重试原业务请求一次。
5. 重试仍失败：报告原接口的实际错误，不继续试探认证方式。

## 微信扫码登录

1. `POST /wxLoginQrcode`，成功响应包含 `data.uuid` 和 `data.qrUrl`。
2. 使用当前 Agent 能够展示图片的方式向用户显示 `qrUrl`，提示用户使用微信扫码并选择完整服务；快照模式不完成注册或登录。
3. 每 5 秒 `POST /checkWXLogin`，以表单传递 `uuid=<uuid>`。
4. 未扫码时返回 `code=="0"`、`msg=未登录`；扫码成功时返回 `code=="1"`、`data.userna`，token 位于同一次响应的 `Set-Cookie` 中。
5. 扫码结果保留 5 分钟；遇到“请求过于频繁”时把轮询间隔增加到 10 秒。

二维码也可以通过 `GET /wxLoginQrcode/<uuid>.png` 获取。未注册用户完成授权后会自动注册；登录成功后提醒用户在网站账户设置中完善账户安全设置。

## 账号密码登录

`POST /doLogin`

Content-Type：`application/x-www-form-urlencoded`

- `userna`：账号，必填。
- `passwd`：用户原始密码按 UTF-8 计算的 MD5 小写十六进制，必填。
- `device`：浏览器登录不传；移动端登录时传设备标识。

成功时 `code=="1"`，token 位于响应的 `Set-Cookie` 中。密码只用于本次请求，使用后立即丢弃，不写入配置、日志或答复。

## 保存与校验 token

将 token 保存到用户目录 `.fabao/auth.json`，只保存 token，不保存密码：

```json
{"baseUrl":"https://fabaotu.com","token":"<token>","username":"<账号名>","loginTime":"<当前时间>"}
```

`username` 优先使用扫码响应的 `data.userna` 或账号密码登录时的账号，无法取得时写“微信登录”。

只有用户明确要求单独检查登录状态，并且当前没有可执行的业务请求时，才携带 Cookie 调用 `POST /laws/getLawText` 并以表单传递 `lawId=1`；`code=="1"` 表示有效。只要任一业务请求已经返回“请先登录”或“请重新登录”，就不得再执行该校验。禁止调用 `/loginCheck`，该接口会校验设备指纹，不同调用环境可能清理会话。

## 秘密保护

- 用户直接在对话或接口参数中提供完整的百度 OCR API Key、Secret Key 时，按法律文件解析参考中的流程为当前登录账户完成验证和保存；不追加安全提示。
- 不在命令输出、日志、生成文档或最终答复中展示 token、密码或密钥。
- 百度 OCR 凭据可在网站账户设置或 Agent 对话中配置；未配置不是错误，文件解析会自动降级。
