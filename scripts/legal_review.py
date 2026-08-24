#!/usr/bin/env python3
import argparse
import datetime
import getpass
import hashlib
from http.cookies import SimpleCookie
import json
import mimetypes
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

OFFICIAL_SERVICE_URL = "https://fabaotu.com"
OFFICIAL_SERVICE_HOST = urllib.parse.urlparse(OFFICIAL_SERVICE_URL).hostname
DEFAULT_BASE_URL = OFFICIAL_SERVICE_URL
SESSION_COOKIE_NAME = "fabao"
AUTH_DIRECTORY_NAME = ".xunfa"
UPDATE_CHECK_FILE_NAME = "update-check.json"
BASE_URL_ENV_NAME = "XUNFA_BASE_URL"
OCR_CREDENTIAL_PATH = "/user/ocrCredential"
LOOPBACK_HOSTS = ("localhost", "127.0.0.1", "::1")
AUTH_REQUIRED_EXIT = 3
REQUEST_FAILED_EXIT = 4
INPUT_FAILED_EXIT = 5
UPLOAD_TIMEOUT_SECONDS = 300
LAW_TIMEOUT_SECONDS = 60
UPDATE_FETCH_TIMEOUT_SECONDS = 3
UPLOAD_CHUNK_SIZE = 1024 * 1024
AUTH_MESSAGES = ("请先登录", "请重新登录")
DOCX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
UPDATE_NOTICE_MESSAGE = "检测到寻法技能有新版本，回复“更新寻法”即可拉取。"
ARTICLE_PATTERN = re.compile(r"第[〇零一二三四五六七八九十百千万两\d０-９]{1,12}条(?:之[〇零一二三四五六七八九十百千万两\d０-９]{1,6})?")
LAW_PATTERN = re.compile(r"《([^》\r\n]{2,80})》")
ID_PATTERN = re.compile(r"(?:公民身份号码|身份证(?:号码|号)?)[：: \t]*([0-9Xx]+)(?![0-9A-Za-z])")
USCC_PATTERN = re.compile(r"(?:统一社会信用代码|社会信用代码)[：: \t]*([0-9A-Za-z]+)(?![0-9A-Za-z])")
MOBILE_PATTERN = re.compile(r"(?:手机号码|手机号)[：: \t]*([0-9][0-9 \t\u3000-]{4,30})")
BANK_CARD_PATTERN = re.compile(r"银行卡号[：: \t]*([0-9][0-9 \t\u3000-]{10,45})")
DATE_PATTERN = re.compile(r"(?<!\d)(\d{4})[年\-/\.](\d{1,2})[月\-/\.](\d{1,2})日?(?!\d)")
PLACEHOLDER_PATTERN = re.compile(r"\$\{[^{}]+}|\{\{[^{}]+}}|\[(?:姓名|日期|金额|地址|待填写|TODO)\]|(?:待填写|待补充|待补|此处填写)")
REGION_PREFIXES = {
    "11", "12", "13", "14", "15", "21", "22", "23", "31", "32", "33", "34", "35", "36", "37",
    "41", "42", "43", "44", "45", "46", "50", "51", "52", "53", "54", "61", "62", "63", "64", "65",
    "71", "81", "82",
}
ID_WEIGHTS = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
ID_CHECK_CODES = "10X98765432"
USCC_CHARS = "0123456789ABCDEFGHJKLMNPQRTUWXY"
USCC_WEIGHTS = (1, 3, 9, 27, 19, 26, 16, 17, 20, 29, 25, 13, 8, 24, 10, 30, 28)
COMMON_TYPOS = {
    "赔尝": "赔偿",
    "起诉壮": "起诉状",
    "法侓": "法律",
    "辨称": "辩称",
    "撤销权力人": "撤销权利人",
}
NON_LAW_TITLE_SUFFIXES = ("合同", "协议", "章程", "起诉状", "上诉状", "答辩状", "判决书", "裁定书", "申请书", "委托书", "承诺书", "借条", "欠条")
ARTICLE_QUERY_PATTERN = re.compile(
    r"^第?([〇零一二三四五六七八九十百千万两\d０-９]{1,12})条?(?:之([〇零一二三四五六七八九十百千万两\d０-９]{1,6}))?$"
)
FULL_WIDTH_DIGIT_TABLE = str.maketrans("０１２３４５６７８９", "0123456789")


def sanitize_error_message(value):
    message = str(value or "接口请求失败").replace("\r", " ").replace("\n", " ")
    return message[:300]


class ReviewError(Exception):
    def __init__(self, status, message, exit_code):
        super().__init__(message)
        self.status = status
        self.message = message
        self.exit_code = exit_code


class MultipartBody:
    def __init__(self, file_parts, suffix):
        self.file_parts = file_parts
        self.suffix = suffix
        self.content_length = sum(len(prefix) + file_path.stat().st_size
                                  for file_path, prefix, _ in file_parts) + len(suffix)
        self.sha256 = None

    def __len__(self):
        return self.content_length

    def __iter__(self):
        actual_hashes = []
        for file_path, prefix, expected_sha256 in self.file_parts:
            digest = hashlib.sha256()
            bytes_read = 0
            expected_size = file_path.stat().st_size
            yield prefix
            with file_path.open("rb") as file:
                while True:
                    chunk = file.read(UPLOAD_CHUNK_SIZE)
                    if not chunk:
                        break
                    bytes_read += len(chunk)
                    digest.update(chunk)
                    yield chunk
            actual_sha256 = digest.hexdigest()
            if bytes_read != expected_size or actual_sha256 != expected_sha256:
                raise ReviewError("input_failed", "上传快照在发送期间发生变化", INPUT_FAILED_EXIT)
            actual_hashes.append(actual_sha256)
        yield self.suffix
        self.sha256 = actual_hashes


class XunfaClient:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.last_headers = None

    def require_token(self):
        if not self.token:
            raise ReviewError("auth_missing", "没有可用登录态", AUTH_REQUIRED_EXIT)

    def send_json(self, path, body, method="POST", timeout=LAW_TIMEOUT_SECONDS):
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers = {"Content-Type": "application/json; charset=utf-8", "Accept": "application/json"}
        return self.send(path, payload, headers, timeout, method)

    def send_form(self, path, values, timeout=LAW_TIMEOUT_SECONDS):
        payload = urllib.parse.urlencode(values, doseq=True).encode("utf-8")
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8", "Accept": "application/json"}
        return self.send(path, payload, headers, timeout)

    def send_binary(self, path, body, headers, timeout, method="POST"):
        request_headers = dict(headers)
        if self.token:
            request_headers["Cookie"] = SESSION_COOKIE_NAME + "=" + self.token
        request = urllib.request.Request(self.base_url + path, data=body, headers=request_headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                self.last_headers = response.headers
                raw = response.read()
        except urllib.error.HTTPError as error:
            raw = error.read()
            result = parse_json_response(raw)
            if is_auth_required(result):
                raise ReviewError("auth_required", str(result.get("msg", "请先登录")), AUTH_REQUIRED_EXIT) from error
            message = result.get("msg") if isinstance(result, dict) else raw.decode("utf-8", errors="replace")
            raise ReviewError("request_failed", sanitize_error_message(message or error), REQUEST_FAILED_EXIT) from error
        except urllib.error.URLError as error:
            raise ReviewError("request_failed", sanitize_error_message(error.reason), REQUEST_FAILED_EXIT) from error
        except TimeoutError as error:
            raise ReviewError("request_failed", "接口请求超时", REQUEST_FAILED_EXIT) from error
        result = parse_json_response(raw)
        if is_auth_required(result):
            raise ReviewError("auth_required", str(result.get("msg", "请先登录")), AUTH_REQUIRED_EXIT)
        return raw, self.last_headers

    def upload_and_parse(self, file_paths):
        self.require_token()
        if not file_paths:
            raise ReviewError("input_failed", "至少需要一个输入文件", INPUT_FAILED_EXIT)
        with tempfile.TemporaryDirectory(prefix="xunfa-upload-") as temporary_directory:
            snapshots = [create_upload_snapshot(file_path, Path(temporary_directory), index)
                         for index, file_path in enumerate(file_paths)]
            snapshot_paths = [item[0] for item in snapshots]
            source_sha256 = [item[1] for item in snapshots]
            boundary = "----XunfaSkill" + uuid.uuid4().hex
            body = build_multipart_body(snapshot_paths, boundary, [file_path.name for file_path in file_paths], source_sha256)
            headers = {
                "Content-Type": "multipart/form-data; boundary=" + boundary,
                "Accept": "application/json",
                "Content-Length": str(len(body)),
            }
            response = self.send("/file/MultipartFiles/uploadAndParse", body, headers, UPLOAD_TIMEOUT_SECONDS)
            if body.sha256 != source_sha256:
                raise ReviewError("request_failed", "上传文件未完整读取", REQUEST_FAILED_EXIT)
        data = require_success(response)
        if not isinstance(data, list) or len(data) != len(file_paths):
            raise ReviewError("parse_failed", "文件解析接口没有返回文件结果", REQUEST_FAILED_EXIT)
        return data, source_sha256

    def search_laws_batch(self, queries):
        if not queries:
            return []
        self.require_token()
        response = self.send_json("/laws/searchByLawBatch", queries)
        return require_success(response)

    def send(self, path, body, headers, timeout, method="POST"):
        request_headers = dict(headers)
        if self.token:
            request_headers["Cookie"] = SESSION_COOKIE_NAME + "=" + self.token
        request = urllib.request.Request(self.base_url + path, data=body, headers=request_headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                self.last_headers = response.headers
                raw = response.read()
        except urllib.error.HTTPError as error:
            raw = error.read()
            result = parse_json_response(raw)
            if is_auth_required(result):
                raise ReviewError("auth_required", str(result.get("msg", "请先登录")), AUTH_REQUIRED_EXIT) from error
            if isinstance(result, dict):
                message = result.get("msg") or error
            else:
                message = raw.decode("utf-8", errors="replace") or str(error)
            raise ReviewError("request_failed", sanitize_error_message(message), REQUEST_FAILED_EXIT) from error
        except urllib.error.URLError as error:
            raise ReviewError("request_failed", sanitize_error_message(error.reason), REQUEST_FAILED_EXIT) from error
        except TimeoutError as error:
            raise ReviewError("request_failed", "接口请求超时", REQUEST_FAILED_EXIT) from error
        result = parse_json_response(raw)
        if result is None:
            raise ReviewError("request_failed", "接口没有返回有效 JSON", REQUEST_FAILED_EXIT)
        if is_auth_required(result):
            raise ReviewError("auth_required", str(result.get("msg", "请先登录")), AUTH_REQUIRED_EXIT)
        return result


def create_upload_snapshot(file_path, temporary_directory, index=0):
    suffix = file_path.suffix.lower()
    if not re.fullmatch(r"\.[a-z0-9]{1,10}", suffix):
        suffix = ".bin"
    snapshot_path = temporary_directory / ("upload-" + str(index) + suffix)
    try:
        before = file_path.stat()
        digest = hashlib.sha256()
        bytes_read = 0
        with file_path.open("rb") as source, snapshot_path.open("xb") as target:
            while True:
                chunk = source.read(UPLOAD_CHUNK_SIZE)
                if not chunk:
                    break
                bytes_read += len(chunk)
                digest.update(chunk)
                target.write(chunk)
            target.flush()
            os.fsync(target.fileno())
        after = file_path.stat()
        if (bytes_read != before.st_size or before.st_size != after.st_size
                or before.st_mtime_ns != after.st_mtime_ns):
            raise ReviewError("input_failed", "输入文件在读取期间发生变化，请保存后重试", INPUT_FAILED_EXIT)
        os.chmod(snapshot_path, 0o600)
        return snapshot_path, digest.hexdigest()
    except ReviewError:
        raise
    except OSError as error:
        raise ReviewError("input_failed", "无法创建上传快照", INPUT_FAILED_EXIT) from error


def build_multipart_body(file_paths, boundary, display_names, expected_sha256):
    if not (len(file_paths) == len(display_names) == len(expected_sha256)):
        raise ReviewError("input_failed", "上传文件参数数量不一致", INPUT_FAILED_EXIT)
    lines = []

    def add_text_field(name, value):
        lines.append(("--" + boundary + "\r\n").encode("ascii"))
        lines.append((f'Content-Disposition: form-data; name="{name}"\r\n\r\n').encode("ascii"))
        lines.append(str(value).encode("utf-8"))
        lines.append(b"\r\n")

    add_text_field("outputFormat", "plain")
    add_text_field("needText", "true")
    add_text_field("saveRecord", "false")
    common_prefix = b"".join(lines)
    file_parts = []
    for index, (file_path, display_name, digest) in enumerate(zip(file_paths, display_names, expected_sha256)):
        suffix = file_path.suffix.lower()
        if not re.fullmatch(r"\.[a-z0-9]{1,10}", suffix):
            suffix = ".bin"
        fallback_name = "upload" + suffix
        encoded_name = urllib.parse.quote(display_name, safe="")
        content_type = mimetypes.guess_type(display_name)[0] or "application/octet-stream"
        separator = common_prefix if index == 0 else b"\r\n"
        header = ("--" + boundary + "\r\n").encode("ascii")
        disposition = (
            f'Content-Disposition: form-data; name="files"; filename="{fallback_name}"; '
            f"filename*=UTF-8''{encoded_name}\r\n"
        ).encode("ascii")
        file_parts.append((file_path, separator + header + disposition
                           + ("Content-Type: " + content_type + "\r\n\r\n").encode("ascii"), digest))
    suffix_bytes = b"\r\n" + ("--" + boundary + "--\r\n").encode("ascii")
    return MultipartBody(file_parts, suffix_bytes)


def parse_json_response(raw):
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def require_success(response):
    if not isinstance(response, dict):
        raise ReviewError("request_failed", "接口响应格式错误", REQUEST_FAILED_EXIT)
    if str(response.get("code")) != "1":
        raise ReviewError("request_failed", sanitize_error_message(response.get("msg")), REQUEST_FAILED_EXIT)
    return response.get("data")


def is_auth_required(response):
    if not isinstance(response, dict) or str(response.get("code")) == "1":
        return False
    message = str(response.get("msg", ""))
    return any(value in message for value in AUTH_MESSAGES)


def load_auth(base_url):
    auth_path = Path.home() / AUTH_DIRECTORY_NAME / "auth.json"
    auth = {}
    if auth_path.exists():
        try:
            auth = json.loads(read_text_exact(auth_path).lstrip("\ufeff"))
        except (OSError, json.JSONDecodeError) as error:
            raise ReviewError("input_failed", "auth.json 不是有效 JSON", INPUT_FAILED_EXIT) from error
        if not isinstance(auth, dict):
            raise ReviewError("input_failed", "auth.json 必须是 JSON 对象", INPUT_FAILED_EXIT)
    token = str(auth.get("token", "")).strip()
    if token:
        auth_base_url = str(auth.get("baseUrl") or DEFAULT_BASE_URL).strip()
        if service_origin(base_url) != service_origin(resolve_base_url(auth_base_url)):
            return ""
    return token


def save_auth(base_url, token, username):
    value = str(token or "").strip()
    if not value:
        raise ReviewError("request_failed", "登录响应未包含登录态", REQUEST_FAILED_EXIT)
    auth_dir = Path.home() / AUTH_DIRECTORY_NAME
    auth_dir.mkdir(parents=True, exist_ok=True)
    auth_path = auth_dir / "auth.json"
    payload = {
        "baseUrl": str(base_url).rstrip("/"),
        "token": value,
        "username": str(username or "微信登录"),
        "loginTime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=auth_dir, delete=False) as temporary_file:
            temporary_file.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
            temporary_path = Path(temporary_file.name)
        os.chmod(temporary_path, 0o600)
        os.replace(temporary_path, auth_path)
    except OSError as error:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink(missing_ok=True)
        raise ReviewError("request_failed", "无法保存登录态", REQUEST_FAILED_EXIT) from error


def get_update_check_path():
    return Path.home() / AUTH_DIRECTORY_NAME / UPDATE_CHECK_FILE_NAME


def read_update_check_date(path):
    try:
        data = json.loads(read_text_exact(path).lstrip("\ufeff"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    value = data.get("date")
    return value if isinstance(value, str) else None


def write_update_check_date(path, date_value):
    temporary_path = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as temporary_file:
            temporary_file.write(json.dumps({"date": date_value}, ensure_ascii=False, separators=(",", ":")))
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
            temporary_path = Path(temporary_file.name)
        os.replace(temporary_path, path)
        return True
    except OSError:
        return False
    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink(missing_ok=True)


def run_git_command(command, skill_directory, timeout=UPDATE_FETCH_TIMEOUT_SECONDS):
    return subprocess.run(
        command,
        cwd=str(skill_directory),
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def check_daily_update(skill_directory=None, state_path=None, today=None, command_runner=None):
    date_value = today or datetime.date.today().isoformat()
    marker_path = Path(state_path) if state_path else get_update_check_path()
    if read_update_check_date(marker_path) == date_value:
        return None
    if not write_update_check_date(marker_path, date_value):
        return None
    runner = command_runner or run_git_command
    root_directory = Path(skill_directory) if skill_directory else Path(__file__).resolve().parent.parent
    try:
        fetched = runner(["git", "fetch", "--quiet"], root_directory)
        if fetched.returncode != 0:
            return None
        local = runner(["git", "rev-parse", "HEAD"], root_directory)
        upstream = runner(["git", "rev-parse", "@{u}"], root_directory)
        if local.returncode != 0 or upstream.returncode != 0:
            return None
        local_commit = local.stdout.strip()
        upstream_commit = upstream.stdout.strip()
        if not local_commit or not upstream_commit or local_commit == upstream_commit:
            return None
        can_fast_forward = runner(["git", "merge-base", "--is-ancestor", "HEAD", "@{u}"], root_directory)
        if can_fast_forward.returncode != 0:
            return None
        return {"available": True, "message": UPDATE_NOTICE_MESSAGE}
    except (OSError, subprocess.SubprocessError):
        return None


def extract_cookie_token(headers):
    if headers is None:
        return ""
    cookie = SimpleCookie()
    for value in headers.get_all("Set-Cookie", []):
        cookie.load(value)
    item = cookie.get(SESSION_COOKIE_NAME)
    return item.value.strip() if item is not None else ""


def resolve_base_url(value):
    configured = value or os.environ.get(BASE_URL_ENV_NAME) or DEFAULT_BASE_URL
    parsed = urllib.parse.urlparse(configured)
    try:
        port = parsed.port
    except ValueError as error:
        raise ReviewError("input_failed", "服务地址端口格式错误", INPUT_FAILED_EXIT) from error
    if (parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password
            or parsed.query or parsed.fragment):
        raise ReviewError("input_failed", "服务地址格式错误", INPUT_FAILED_EXIT)
    host = parsed.hostname.lower()
    if host == OFFICIAL_SERVICE_HOST:
        if parsed.scheme != "https" or port not in (None, 443):
            raise ReviewError("input_failed", "寻法正式服务只允许使用 HTTPS 默认端口", INPUT_FAILED_EXIT)
    elif host not in LOOPBACK_HOSTS:
        raise ReviewError("input_failed", "服务地址只允许寻法正式服务或本机回环地址", INPUT_FAILED_EXIT)
    return configured.rstrip("/")


def service_origin(value):
    parsed = urllib.parse.urlparse(value)
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    return parsed.scheme.lower(), parsed.hostname.lower(), port


def read_text_exact(path):
    with path.open("r", encoding="utf-8", newline="") as file:
        return file.read()


def write_text_exact(path, text):
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", prefix=".review-",
                                         suffix=".tmp", dir=path.parent, delete=False) as file:
            file.write(text)
            file.flush()
            os.fsync(file.fileno())
            temporary_path = Path(file.name)
        os.chmod(temporary_path, 0o600)
        try:
            os.link(temporary_path, path)
        except FileExistsError as error:
            raise ReviewError("input_failed", "输出文件已存在，请使用新的输出路径", INPUT_FAILED_EXIT) from error
        except OSError as error:
            raise ReviewError("input_failed", "输出目录不支持安全的新文件写入", INPUT_FAILED_EXIT) from error
    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()


def resolve_output_path(value, protected_paths):
    output_path = Path(value).resolve()
    output_key = os.path.normcase(str(output_path))
    for protected_path in protected_paths:
        if output_key == os.path.normcase(str(Path(protected_path).resolve())):
            raise ReviewError("input_failed", "输出路径不能覆盖输入文件", INPUT_FAILED_EXIT)
    if output_path.exists():
        raise ReviewError("input_failed", "输出文件已存在，请使用新的输出路径", INPUT_FAILED_EXIT)
    probe_path = None
    probe_link_path = None
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if not output_path.parent.is_dir():
            raise OSError("输出父路径不是目录")
        with tempfile.NamedTemporaryFile(prefix=".review-probe-", suffix=".tmp", dir=output_path.parent,
                                         delete=False) as file:
            probe_path = Path(file.name)
        probe_link_path = output_path.parent / (".review-link-" + uuid.uuid4().hex + ".tmp")
        os.link(probe_path, probe_link_path)
    except OSError as error:
        raise ReviewError("input_failed", "输出目录不支持安全的新文件写入", INPUT_FAILED_EXIT) from error
    finally:
        if probe_link_path and probe_link_path.exists():
            probe_link_path.unlink()
        if probe_path and probe_path.exists():
            probe_path.unlink()
    return output_path


def write_json(path, data):
    write_text_exact(path, json.dumps(data, ensure_ascii=False, indent=2))


def read_json(path):
    try:
        return json.loads(read_text_exact(path).lstrip("\ufeff"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReviewError("input_failed", f"无法读取 JSON: {path}", INPUT_FAILED_EXIT) from error


def extract_citations(text):
    citations = {}
    law_matches = list(LAW_PATTERN.finditer(text))
    for match_index, law_match in enumerate(law_matches):
        next_law_start = law_matches[match_index + 1].start() if match_index + 1 < len(law_matches) else len(text)
        segment_end = min(next_law_start, law_match.end() + 180)
        segment = text[law_match.end():segment_end]
        stop = re.search(r"[。；;\r\n]", segment)
        if stop:
            segment = segment[:stop.start()]
        law_name = law_match.group(1).strip()
        if law_name.endswith(NON_LAW_TITLE_SUFFIXES):
            continue
        articles = list(ARTICLE_PATTERN.finditer(segment))
        for article in articles:
            article_number = article.group(0)
            key = law_name + "\u0000" + article_number
            citations.setdefault(key, {
                "lawName": law_name,
                "articleNumber": article_number,
            })
    return list(citations.values())


def make_issue(category, start, end, original, problem, replacement=None, status="needs_input"):
    return {
        "category": category,
        "start": start,
        "end": end,
        "original": original,
        "displayOriginal": original,
        "problem": problem,
        "replacement": replacement,
        "replacementStatus": status,
    }


def validate_id_card(value):
    normalized = value.upper()
    if len(normalized) != 18 or not re.fullmatch(r"[0-9]{17}[0-9X]", normalized):
        return "身份证号格式或长度不符合规则"
    if normalized[:2] not in REGION_PREFIXES:
        return "身份证号地区码不符合规则"
    try:
        birth_date = datetime.datetime.strptime(normalized[6:14], "%Y%m%d").date()
    except ValueError:
        return "身份证号出生日期不符合规则"
    if birth_date > datetime.date.today():
        return "身份证号出生日期晚于当前日期"
    if normalized[14:17] == "000":
        return "身份证号顺序码不能为 000"
    total = sum(int(normalized[index]) * ID_WEIGHTS[index] for index in range(17))
    expected = ID_CHECK_CODES[total % 11]
    if normalized[-1] != expected:
        return "身份证号校验码错误"
    return None


def validate_uscc(value):
    normalized = value.upper()
    if len(normalized) != 18:
        return "统一社会信用代码长度不符合规则"
    if len(set(normalized)) == 1:
        return "统一社会信用代码不能全部为同一字符"
    if any(character not in USCC_CHARS for character in normalized):
        return "统一社会信用代码包含非法字符"
    total = sum(USCC_CHARS.index(normalized[index]) * USCC_WEIGHTS[index] for index in range(17))
    expected = USCC_CHARS[(31 - total % 31) % 31]
    if normalized[-1] != expected:
        return "统一社会信用代码校验码错误"
    return None


def parse_chinese_number(value):
    value = value.translate(FULL_WIDTH_DIGIT_TABLE)
    if value.isdigit():
        return int(value)
    digits = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4,
              "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
    if all(character in digits for character in value):
        return int("".join(str(digits[character]) for character in value))
    units = {"十": 10, "百": 100, "千": 1000}
    total = 0
    section = 0
    number = 0
    for character in value:
        if character in digits:
            number = digits[character]
        elif character in units:
            section += (number or 1) * units[character]
            number = 0
        elif character == "万":
            section += number
            total += (section or 1) * 10000
            section = 0
            number = 0
        else:
            return None
    return total + section + number


def normalize_article_query_key(value):
    normalized = re.sub(r"\s+", "", value.translate(FULL_WIDTH_DIGIT_TABLE))
    match = ARTICLE_QUERY_PATTERN.fullmatch(normalized)
    if not match:
        return normalized
    article = parse_chinese_number(match.group(1))
    suffix = parse_chinese_number(match.group(2)) if match.group(2) else None
    if article is None or (match.group(2) and suffix is None):
        return normalized
    return str(article) + (":" + str(suffix) if suffix is not None else "")


def collect_rule_issues(text):
    issues = []
    for match in ID_PATTERN.finditer(text):
        value = match.group(1)
        if match.end(1) < len(text) and text[match.end(1)] == "*":
            continue
        problem = validate_id_card(value)
        if problem:
            issues.append(make_issue("事实错误", match.start(1), match.end(1), value, problem))

    for match in USCC_PATTERN.finditer(text):
        value = match.group(1).upper()
        if match.end(1) < len(text) and text[match.end(1)] == "*":
            continue
        problem = validate_uscc(value)
        if problem:
            issues.append(make_issue("事实错误", match.start(1), match.end(1), match.group(1), problem))

    for match in MOBILE_PATTERN.finditer(text):
        raw = match.group(1).rstrip(" \t\u3000-")
        digit_count = 0
        candidate_end = len(raw)
        for digit_match in re.finditer(r"\d+", raw):
            digit_count += len(digit_match.group(0))
            if digit_count >= 11:
                candidate_end = digit_match.end()
                break
        raw = raw[:candidate_end]
        value = re.sub(r"[ \t\u3000-]", "", raw)
        grouping_valid = re.fullmatch(r"\d{11}|\d{3}[ \t\u3000-]\d{4}[ \t\u3000-]\d{4}", raw)
        if not grouping_valid or not re.fullmatch(r"1[3-9]\d{9}", value):
            issues.append(make_issue("事实错误", match.start(1), match.start(1) + len(raw), raw,
                                     "手机号码格式不符合规则"))

    for match in BANK_CARD_PATTERN.finditer(text):
        raw = match.group(1).rstrip(" \t\u3000-")
        value = re.sub(r"[ \t\u3000-]", "", raw)
        groups = re.split(r"[ \t\u3000-]+", raw)
        grouping_valid = len(groups) == 1 or (
            len(groups) >= 3 and all(len(group) == 4 for group in groups[:-1]) and len(groups[-1]) in (3, 4)
        )
        if not value.isdigit() or not 12 <= len(value) <= 19 or not grouping_valid:
            issues.append(make_issue("事实错误", match.start(1), match.start(1) + len(raw), raw,
                                     "银行卡号格式不符合规则"))

    for match in DATE_PATTERN.finditer(text):
        try:
            datetime.date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            issues.append(make_issue("事实错误", match.start(), match.end(), match.group(0),
                                     "日期不存在或格式中的年月日超出范围"))

    for match in PLACEHOLDER_PATTERN.finditer(text):
        issues.append(make_issue("结构错误", match.start(), match.end(), match.group(0),
                                 "存在未替换的模板占位内容"))

    for wrong, correct in COMMON_TYPOS.items():
        for match in re.finditer(re.escape(wrong), text):
            issues.append(make_issue("错别字", match.start(), match.end(), wrong,
                                     "高置信度常见错词", correct, "ready"))

    issues.extend(find_unbalanced_punctuation(text))
    return deduplicate_issues(issues)


def find_unbalanced_punctuation(text):
    issues = []
    pairs = (("（", "）"), ("《", "》"), ("“", "”"), ("‘", "’"))
    for left, right in pairs:
        open_positions = []
        unmatched_closers = []
        for index, character in enumerate(text):
            if character == left:
                open_positions.append(index)
            elif character == right:
                if open_positions:
                    open_positions.pop()
                else:
                    unmatched_closers.append(index)
        unmatched_positions = unmatched_closers + open_positions
        if not unmatched_positions:
            continue
        start = min(unmatched_positions)
        problem = f"{left}{right} 未正确配对，缺少左侧 {len(unmatched_closers)} 个，缺少右侧 {len(open_positions)} 个"
        issues.append(make_issue("病句", start, min(start + 1, len(text)), text[start:start + 1], problem))
    return issues


def deduplicate_issues(issues):
    unique = {}
    for issue in issues:
        key = (issue["category"], issue["start"], issue["end"], issue["problem"])
        unique[key] = issue
    return sorted(unique.values(), key=lambda item: (item["start"], item["category"]))


def build_document_context(source, text):
    return {
        "source": source,
        "text": text,
        "textSha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "citations": extract_citations(text),
        "ruleIssues": collect_rule_issues(text),
    }


def prepare_command(args):
    documents = []
    item_errors = []
    if args.files:
        source_paths = [Path(value).resolve() for value in args.files]
        if len(set(source_paths)) != len(source_paths):
            raise ReviewError("input_failed", "输入文件不能重复", INPUT_FAILED_EXIT)
        for source_path in source_paths:
            if not source_path.is_file():
                raise ReviewError("input_failed", "输入文件不存在", INPUT_FAILED_EXIT)
            if source_path.stat().st_size == 0:
                raise ReviewError("input_failed", "输入文件不能为空", INPUT_FAILED_EXIT)
        output_path = resolve_output_path(args.output, source_paths)
        base_url = resolve_base_url(args.base_url)
        client = XunfaClient(base_url, load_auth(base_url))
        parsed_items, source_hashes = client.upload_and_parse(source_paths)
        for index, (source_path, parsed, source_sha256) in enumerate(zip(source_paths, parsed_items, source_hashes), start=1):
            if not isinstance(parsed, dict):
                item_errors.append({"documentNumber": index, "name": source_path.name, "error": "文件解析结果格式错误"})
                continue
            if parsed.get("error"):
                item_errors.append({"documentNumber": index, "name": source_path.name,
                                    "error": sanitize_error_message(parsed.get("error"))})
                continue
            text = parsed.get("textContent")
            if not isinstance(text, str) or not text.strip():
                item_errors.append({"documentNumber": index, "name": source_path.name, "error": "文件解析结果为空"})
                continue
            source = {
                "type": "file",
                "name": source_path.name,
                "path": str(source_path),
                "sha256": source_sha256,
                "ocrProvider": parsed.get("ocrProvider"),
            }
            documents.append(build_document_context(source, text))
    else:
        source_path = Path(args.text_file).resolve()
        if not source_path.is_file():
            raise ReviewError("input_failed", "文本文件不存在", INPUT_FAILED_EXIT)
        output_path = resolve_output_path(args.output, [source_path])
        text = read_text_exact(source_path)
        source = {
            "type": "text",
            "name": source_path.name,
            "path": str(source_path),
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        }
        documents.append(build_document_context(source, text))
    if not documents:
        raise ReviewError("parse_failed", "所有文件均未解析出可检查文本", REQUEST_FAILED_EXIT)
    context = {
        "version": 3,
        "status": "partial" if item_errors else "ok",
        "documents": documents,
        "itemErrors": item_errors,
    }
    write_json(output_path, context)
    return {"status": context["status"], "output": str(output_path), "documents": len(documents),
            "itemErrors": len(item_errors), "citations": sum(len(item["citations"]) for item in documents),
            "ruleIssues": sum(len(item["ruleIssues"]) for item in documents)}


def load_queries(args):
    if args.queries:
        data = read_json(Path(args.queries).resolve())
        if isinstance(data, dict):
            data = data.get("queries")
        if not isinstance(data, list):
            raise ReviewError("input_failed", "queries 必须是 JSON 数组", INPUT_FAILED_EXIT)
        raw_queries = data
    else:
        context = read_json(Path(args.context).resolve())
        if not isinstance(context, dict):
            raise ReviewError("input_failed", "context 必须是 JSON 对象", INPUT_FAILED_EXIT)
        documents = context.get("documents")
        if not isinstance(documents, list):
            raise ReviewError("input_failed", "context 中没有 documents", INPUT_FAILED_EXIT)
        raw_queries = []
        for document in documents:
            if not isinstance(document, dict) or not isinstance(document.get("citations"), list):
                raise ReviewError("input_failed", "context 中的 documents 格式错误", INPUT_FAILED_EXIT)
            raw_queries.extend(document["citations"])
    if not isinstance(raw_queries, list):
        raise ReviewError("input_failed", "法条查询数据必须是 JSON 数组", INPUT_FAILED_EXIT)
    queries = []
    seen = set()
    for index, item in enumerate(raw_queries):
        if not isinstance(item, dict):
            raise ReviewError("input_failed", f"第 {index + 1} 项法条查询不是 JSON 对象", INPUT_FAILED_EXIT)
        law_name_value = item.get("lawName")
        article_number = item.get("articleNumber")
        if not isinstance(law_name_value, str) or not isinstance(article_number, str):
            raise ReviewError("input_failed", f"第 {index + 1} 项法名和条号必须是字符串", INPUT_FAILED_EXIT)
        law_name = law_name_value.strip()
        article_number = article_number.strip()
        if not law_name:
            raise ReviewError("input_failed", f"第 {index + 1} 项法条查询缺少 lawName", INPUT_FAILED_EXIT)
        if not article_number:
            raise ReviewError("input_failed", f"第 {index + 1} 项法条查询缺少 articleNumber", INPUT_FAILED_EXIT)
        law_key = re.sub(r"\s+", "", law_name.strip("《》〈〉"))
        key = (law_key, normalize_article_query_key(article_number))
        if key in seen:
            continue
        seen.add(key)
        queries.append({"lawName": law_name, "articleNumber": article_number})
    if len(queries) > 50:
        raise ReviewError("input_failed", "单次最多查询 50 条法条", INPUT_FAILED_EXIT)
    return queries


def laws_command(args):
    queries = load_queries(args)
    input_path = Path(args.queries or args.context).resolve()
    output_path = resolve_output_path(args.output, [input_path])
    if not queries:
        write_json(output_path, {"status": "ok", "queries": [], "results": []})
        return {"status": "ok", "output": str(output_path), "queries": 0}
    base_url = resolve_base_url(args.base_url)
    client = XunfaClient(base_url, load_auth(base_url))
    results = client.search_laws_batch(queries)
    if not isinstance(results, list) or len(results) != len(queries):
        raise ReviewError("request_failed", "批量法条响应数量与请求不一致", REQUEST_FAILED_EXIT)
    item_errors = []
    for index, item in enumerate(results):
        if not isinstance(item, dict) or item.get("index") != index:
            raise ReviewError("request_failed", f"批量法条第 {index + 1} 项响应格式错误", REQUEST_FAILED_EXIT)
        if item.get("error"):
            item_errors.append({"index": index, "error": sanitize_error_message(item.get("error"))})
    status = "partial" if item_errors else "ok"
    write_json(output_path, {"status": status, "queries": queries, "results": results, "itemErrors": item_errors})
    return {"status": status, "output": str(output_path), "queries": len(queries), "itemErrors": len(item_errors)}


def apply_command(args):
    context_path = Path(args.context).resolve()
    issues_path = Path(args.issues).resolve()
    context = read_json(context_path)
    if not isinstance(context, dict):
        raise ReviewError("input_failed", "context 必须是 JSON 对象", INPUT_FAILED_EXIT)
    documents = context.get("documents")
    if not isinstance(documents, list) or args.document_number < 1 or args.document_number > len(documents):
        raise ReviewError("input_failed", "documentNumber 超出上下文范围", INPUT_FAILED_EXIT)
    document = documents[args.document_number - 1]
    if not isinstance(document, dict):
        raise ReviewError("input_failed", "指定文书上下文格式错误", INPUT_FAILED_EXIT)
    text = document.get("text")
    if not isinstance(text, str):
        raise ReviewError("input_failed", "context 中没有原始文本", INPUT_FAILED_EXIT)
    issue_data = read_json(issues_path)
    if not isinstance(issue_data, dict):
        raise ReviewError("input_failed", "issues 必须是包含 textSha256 和 issues 的 JSON 对象", INPUT_FAILED_EXIT)
    text_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if issue_data.get("textSha256") != text_sha256 or document.get("textSha256") != text_sha256:
        raise ReviewError("input_failed", "issues 与检查上下文不匹配", INPUT_FAILED_EXIT)
    issues = issue_data.get("issues")
    if not isinstance(issues, list):
        raise ReviewError("input_failed", "issues 必须是 JSON 数组", INPUT_FAILED_EXIT)
    protected_paths = [context_path, issues_path]
    source_path = document.get("source", {}).get("path") if isinstance(document.get("source"), dict) else None
    if source_path:
        protected_paths.append(source_path)
    output_path = resolve_output_path(args.output, protected_paths)
    selected = []
    for index, item in enumerate(issues):
        if not isinstance(item, dict):
            raise ReviewError("input_failed", f"第 {index + 1} 个修改项不是 JSON 对象", INPUT_FAILED_EXIT)
        if not isinstance(item.get("apply"), bool):
            raise ReviewError("input_failed", f"第 {index + 1} 个修改项的 apply 必须是布尔值", INPUT_FAILED_EXIT)
        if item["apply"]:
            selected.append(item)
    if not selected:
        raise ReviewError("no_changes", "没有显式确认的修改项", INPUT_FAILED_EXIT)
    unresolved = [item for item in selected if item.get("replacementStatus") != "ready" or item.get("replacement") is None]
    if unresolved:
        raise ReviewError("needs_input", f"仍有 {len(unresolved)} 项错误缺少确定修改值", INPUT_FAILED_EXIT)
    replacements = []
    for item in selected:
        start = item.get("start")
        end = item.get("end")
        if type(start) is not int or type(end) is not int:
            raise ReviewError("input_failed", "修改项位置必须是整数", INPUT_FAILED_EXIT)
        original = item.get("original")
        replacement = item.get("replacement")
        if (start < 0 or end <= start or end > len(text) or not isinstance(original, str)
                or not original or not isinstance(replacement, str)):
            raise ReviewError("input_failed", "修改项位置或文本格式错误", INPUT_FAILED_EXIT)
        replacements.append((start, end, original, replacement))
    replacements.sort(key=lambda item: item[0])
    last_end = 0
    parts = []
    for start, end, original, replacement in replacements:
        if start < last_end:
            raise ReviewError("input_failed", "修改项存在重叠", INPUT_FAILED_EXIT)
        if text[start:end] != original:
            raise ReviewError("input_failed", "修改项原文与指定位置不一致", INPUT_FAILED_EXIT)
        parts.append(text[last_end:start])
        parts.append(replacement)
        last_end = end
    parts.append(text[last_end:])
    corrected = "".join(parts)
    write_text_exact(output_path, corrected)
    return {"status": "ok", "output": str(output_path), "applied": len(replacements)}


def write_binary_new(path, content):
    try:
        with path.open("xb") as output:
            output.write(content)
    except FileExistsError as error:
        raise ReviewError("input_failed", "输出文件已存在", INPUT_FAILED_EXIT) from error
    except OSError as error:
        raise ReviewError("input_failed", "无法写入输出文件", INPUT_FAILED_EXIT) from error


def load_input_object(value, field_name):
    data = read_json(Path(value).resolve())
    if not isinstance(data, dict):
        raise ReviewError("input_failed", field_name + " 必须是 JSON 对象", INPUT_FAILED_EXIT)
    return data


def create_authenticated_client(args):
    base_url = resolve_base_url(args.base_url)
    return XunfaClient(base_url, load_auth(base_url))


def parse_command(args):
    file_paths = [Path(value).resolve() for value in args.files]
    if not file_paths:
        raise ReviewError("input_failed", "至少需要一个输入文件", INPUT_FAILED_EXIT)
    for file_path in file_paths:
        if not file_path.is_file():
            raise ReviewError("input_failed", "输入文件不存在", INPUT_FAILED_EXIT)
        if file_path.stat().st_size == 0:
            raise ReviewError("input_failed", "输入文件不能为空", INPUT_FAILED_EXIT)
    output_path = resolve_output_path(args.output, file_paths)
    parsed_items, source_hashes = create_authenticated_client(args).upload_and_parse(file_paths)
    result = []
    failed_files = 0
    for file_path, parsed, source_hash in zip(file_paths, parsed_items, source_hashes):
        result.append({"sourcePath": str(file_path), "sourceSha256": source_hash, "result": parsed})
        if (not isinstance(parsed, dict) or parsed.get("error")
                or not isinstance(parsed.get("textContent"), str) or not parsed["textContent"].strip()):
            failed_files += 1
    status = "partial" if failed_files else "ok"
    write_json(output_path, {"status": status, "files": result, "failedFiles": failed_files})
    return {"status": status, "output": str(output_path), "files": len(result), "failedFiles": failed_files}


def laws_query_command(args, path):
    body = load_input_object(args.input, "input")
    output_path = resolve_output_path(args.output, [Path(args.input).resolve()])
    client = create_authenticated_client(args)
    client.require_token()
    response = client.send_form(path, body)
    data = require_success(response)
    write_json(output_path, {"status": "ok", "data": data})
    return {"status": "ok", "output": str(output_path)}


def laws_exact_command(args):
    return laws_query_command(args, "/laws/searchByLaw")


def laws_search_command(args):
    return laws_query_command(args, "/laws/search")


def laws_id_command(args):
    return laws_query_command(args, "/laws/getLawText")


def ocr_status_command(args):
    output_path = resolve_output_path(args.output, [])
    client = create_authenticated_client(args)
    client.require_token()
    response = client.send(OCR_CREDENTIAL_PATH, None, {"Accept": "application/json"}, LAW_TIMEOUT_SECONDS, "GET")
    write_json(output_path, {"status": "ok", "data": require_success(response)})
    return {"status": "ok", "output": str(output_path)}


def read_credentials_from_stdin():
    try:
        credentials = json.loads(sys.stdin.read())
    except json.JSONDecodeError as error:
        raise ReviewError("input_failed", "标准输入必须是 OCR 凭据 JSON", INPUT_FAILED_EXIT) from error
    if not isinstance(credentials, dict):
        raise ReviewError("input_failed", "OCR 凭据必须是 JSON 对象", INPUT_FAILED_EXIT)
    api_key = str(credentials.get("apiKey", "")).strip()
    secret_key = str(credentials.get("secretKey", "")).strip()
    if not api_key or not secret_key:
        raise ReviewError("input_failed", "OCR 凭据缺少 apiKey 或 secretKey", INPUT_FAILED_EXIT)
    return {"apiKey": api_key, "secretKey": secret_key}


def ocr_set_command(args):
    output_path = resolve_output_path(args.output, [])
    client = create_authenticated_client(args)
    client.require_token()
    status = require_success(client.send(OCR_CREDENTIAL_PATH, None, {"Accept": "application/json"}, LAW_TIMEOUT_SECONDS, "GET"))
    if isinstance(status, dict) and status.get("hasKey"):
        write_json(output_path, {"status": "ok", "data": status, "saved": False})
        return {"status": "ok", "output": str(output_path), "saved": False}
    saved = require_success(client.send_json(OCR_CREDENTIAL_PATH, read_credentials_from_stdin(), "PUT"))
    write_json(output_path, {"status": "ok", "data": saved, "saved": True})
    return {"status": "ok", "output": str(output_path), "saved": True}


def ocr_delete_command(args):
    output_path = resolve_output_path(args.output, [])
    client = create_authenticated_client(args)
    client.require_token()
    response = client.send(OCR_CREDENTIAL_PATH, None, {"Accept": "application/json"}, LAW_TIMEOUT_SECONDS, "DELETE")
    write_json(output_path, {"status": "ok", "data": require_success(response)})
    return {"status": "ok", "output": str(output_path)}


def docx_command(args):
    text = sys.stdin.read()
    if not text.strip():
        raise ReviewError("input_failed", "文书正文不能为空", INPUT_FAILED_EXIT)
    protected_paths = []
    settings = {}
    if args.settings:
        settings_path = Path(args.settings).resolve()
        protected_paths.append(settings_path)
        settings = load_input_object(args.settings, "settings")
    output_path = resolve_output_path(args.output, protected_paths)
    if output_path.suffix.lower() != ".docx":
        raise ReviewError("input_failed", "输出文件必须使用 .docx 后缀", INPUT_FAILED_EXIT)
    client = create_authenticated_client(args)
    client.require_token()
    payload = {"text": text, "settings": settings}
    if args.file_name:
        payload["fileName"] = args.file_name
    content, headers = client.send_binary("/file/exportLegalDocx", json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                                          {"Content-Type": "application/json; charset=utf-8", "Accept": DOCX_CONTENT_TYPE},
                                          UPLOAD_TIMEOUT_SECONDS)
    content_type = str(headers.get("Content-Type", "")).lower() if headers else ""
    if not content_type.startswith(DOCX_CONTENT_TYPE) or not content.startswith(b"PK"):
        raise ReviewError("request_failed", "文书生成接口未返回 DOCX 文件", REQUEST_FAILED_EXIT)
    write_binary_new(output_path, content)
    return {"status": "ok", "output": str(output_path), "bytes": len(content)}


def auth_qr_start_command(args):
    output_path = resolve_output_path(args.output, [])
    base_url = resolve_base_url(args.base_url)
    client = XunfaClient(base_url, "")
    data = require_success(client.send_json("/wxLoginQrcode", {}))
    if not isinstance(data, dict) or not data.get("uuid") or not data.get("qrUrl"):
        raise ReviewError("request_failed", "二维码接口没有返回完整登录信息", REQUEST_FAILED_EXIT)
    qr_url = str(data["qrUrl"])
    parsed = urllib.parse.urlparse(qr_url)
    if service_origin(qr_url) != service_origin(base_url):
        raise ReviewError("request_failed", "二维码地址与服务地址不一致", REQUEST_FAILED_EXIT)
    content, headers = client.send_binary(parsed.path + (("?" + parsed.query) if parsed.query else ""), None,
                                          {"Accept": "image/png"}, LAW_TIMEOUT_SECONDS, "GET")
    content_type = str(headers.get("Content-Type", "")).lower() if headers else ""
    if not content_type.startswith("image/png") or not content.startswith(b"\x89PNG"):
        raise ReviewError("request_failed", "二维码接口未返回 PNG 图片", REQUEST_FAILED_EXIT)
    write_binary_new(output_path, content)
    return {"status": "ok", "uuid": str(data["uuid"]), "qrPath": str(output_path)}


def auth_qr_wait_command(args):
    uuid_value = str(args.uuid or "").strip()
    if not uuid_value:
        raise ReviewError("input_failed", "缺少二维码 uuid", INPUT_FAILED_EXIT)
    base_url = resolve_base_url(args.base_url)
    client = XunfaClient(base_url, "")
    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        response = client.send_form("/checkWXLogin", {"uuid": uuid_value})
        if str(response.get("code")) == "1":
            data = response.get("data") if isinstance(response.get("data"), dict) else {}
            save_auth(base_url, extract_cookie_token(client.last_headers), data.get("userna"))
            return {"status": "ok", "username": str(data.get("userna") or "微信登录")}
        if str(response.get("msg", "")) != "未登录":
            raise ReviewError("request_failed", sanitize_error_message(response.get("msg")), REQUEST_FAILED_EXIT)
        time.sleep(args.interval)
    raise ReviewError("auth_required", "等待扫码超时", AUTH_REQUIRED_EXIT)


def auth_password_command(args):
    username = str(args.username or "").strip()
    if not username:
        raise ReviewError("input_failed", "缺少登录账号", INPUT_FAILED_EXIT)
    password = getpass.getpass("密码: ") if args.password_prompt else sys.stdin.readline().rstrip("\r\n")
    if not password:
        raise ReviewError("input_failed", "密码不能为空", INPUT_FAILED_EXIT)
    base_url = resolve_base_url(args.base_url)
    client = XunfaClient(base_url, "")
    password_md5 = hashlib.md5(password.encode("utf-8")).hexdigest()
    response = client.send_form("/doLogin", {"userna": username, "passwd": password_md5})
    data = require_success(response)
    response_username = data.get("userna") if isinstance(data, dict) else username
    save_auth(base_url, extract_cookie_token(client.last_headers), response_username or username)
    return {"status": "ok", "username": str(response_username or username)}


def build_parser():
    parser = argparse.ArgumentParser(description="寻法文件解析与法律工作流客户端")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="解析文书并生成检查上下文")
    source_group = prepare.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--files", nargs="+", help="需要通过寻法接口一次解析的一个或多个法律文件")
    source_group.add_argument("--text-file", help="用户直接提供文本生成的 UTF-8 文件")
    prepare.add_argument("--output", required=True, help="检查上下文 JSON 输出路径")
    prepare.add_argument("--base-url", help="用户明确指定的服务地址")
    prepare.set_defaults(handler=prepare_command)

    laws = subparsers.add_parser("laws", help="一次请求批量核验全部法条")
    query_group = laws.add_mutually_exclusive_group(required=True)
    query_group.add_argument("--context", help="prepare 生成的检查上下文")
    query_group.add_argument("--queries", help="Agent 补充后的法条查询 JSON 数组")
    laws.add_argument("--output", required=True, help="批量法条结果 JSON 输出路径")
    laws.add_argument("--base-url", help="用户明确指定的服务地址")
    laws.set_defaults(handler=laws_command)

    parse = subparsers.add_parser("parse", help="解析一个或多个文件")
    parse.add_argument("--files", nargs="+", required=True, help="需要解析的文件绝对路径")
    parse.add_argument("--output", required=True, help="解析结果 JSON 输出路径")
    parse.add_argument("--base-url", help="用户明确指定的服务地址")
    parse.set_defaults(handler=parse_command)

    for command_name, command_help, handler in (
            ("law-exact", "按完整法名查询法律或法条", laws_exact_command),
            ("law-search", "按关键词发现候选法律", laws_search_command),
            ("law-id", "按可信 lawId 查询法律或法条", laws_id_command)):
        law_command = subparsers.add_parser(command_name, help=command_help)
        law_command.add_argument("--input", required=True, help="请求 JSON 文件路径")
        law_command.add_argument("--output", required=True, help="结果 JSON 输出路径")
        law_command.add_argument("--base-url", help="用户明确指定的服务地址")
        law_command.set_defaults(handler=handler)

    docx = subparsers.add_parser("docx", help="将法律文书纯文本导出为 DOCX")
    docx.add_argument("--settings", help="格式设置 JSON 文件路径")
    docx.add_argument("--file-name", help="文书下载文件名")
    docx.add_argument("--output", required=True, help="新建 DOCX 输出路径")
    docx.add_argument("--base-url", help="用户明确指定的服务地址")
    docx.set_defaults(handler=docx_command)

    ocr_status = subparsers.add_parser("ocr-status", help="查询当前账户 OCR 配置状态")
    ocr_status.add_argument("--output", required=True, help="结果 JSON 输出路径")
    ocr_status.add_argument("--base-url", help="用户明确指定的服务地址")
    ocr_status.set_defaults(handler=ocr_status_command)

    ocr_set = subparsers.add_parser("ocr-set", help="从标准输入读取 JSON 并保存 OCR 凭据")
    ocr_set.add_argument("--output", required=True, help="结果 JSON 输出路径")
    ocr_set.add_argument("--base-url", help="用户明确指定的服务地址")
    ocr_set.set_defaults(handler=ocr_set_command)

    ocr_delete = subparsers.add_parser("ocr-delete", help="删除当前账户 OCR 凭据")
    ocr_delete.add_argument("--output", required=True, help="结果 JSON 输出路径")
    ocr_delete.add_argument("--base-url", help="用户明确指定的服务地址")
    ocr_delete.set_defaults(handler=ocr_delete_command)

    qr_start = subparsers.add_parser("auth-qr-start", help="生成微信登录二维码 PNG")
    qr_start.add_argument("--output", required=True, help="新建二维码 PNG 输出路径")
    qr_start.add_argument("--base-url", help="用户明确指定的服务地址")
    qr_start.set_defaults(handler=auth_qr_start_command)

    qr_wait = subparsers.add_parser("auth-qr-wait", help="等待扫码登录并保存登录态")
    qr_wait.add_argument("--uuid", required=True, help="auth-qr-start 返回的 uuid")
    qr_wait.add_argument("--interval", type=int, default=5, choices=range(1, 61), metavar="1-60", help="轮询间隔秒数")
    qr_wait.add_argument("--timeout", type=int, default=300, choices=range(5, 601), metavar="5-600", help="最长等待秒数")
    qr_wait.add_argument("--base-url", help="用户明确指定的服务地址")
    qr_wait.set_defaults(handler=auth_qr_wait_command)

    password = subparsers.add_parser("auth-password", help="使用账号密码登录并保存登录态")
    password.add_argument("--username", required=True, help="登录账号")
    password.add_argument("--password-prompt", action="store_true", help="在终端安全读取密码")
    password.add_argument("--base-url", help="用户明确指定的服务地址")
    password.set_defaults(handler=auth_password_command)

    apply_parser = subparsers.add_parser("apply", help="只替换确认错误并输出完整修正版")
    apply_parser.add_argument("--context", required=True, help="prepare 生成的检查上下文")
    apply_parser.add_argument("--document-number", required=True, type=int, help="要生成修正版的文书序号，从 1 开始")
    apply_parser.add_argument("--issues", required=True, help="确认修改的问题 JSON")
    apply_parser.add_argument("--output", required=True, help="修正版文本输出路径")
    apply_parser.set_defaults(handler=apply_command)
    return parser


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args()
    update_notice = check_daily_update()
    try:
        result = args.handler(args)
        if update_notice:
            result["updateNotice"] = update_notice
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except ReviewError as error:
        print(json.dumps({"status": error.status, "message": error.message}, ensure_ascii=False), file=sys.stderr)
        return error.exit_code
    except OSError as error:
        print(json.dumps({"status": "input_failed", "message": str(error)}, ensure_ascii=False), file=sys.stderr)
        return INPUT_FAILED_EXIT


if __name__ == "__main__":
    sys.exit(main())
