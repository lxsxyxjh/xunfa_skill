#!/usr/bin/env python3
import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

INPUT_FAILED_EXIT = 5
DOCX_SERVICE_URL = os.environ.get("DOCX_SERVICE_URL", "https://xunfakeji.com/file/exportLegalDocx")

HTML_TAG_PATTERN = re.compile(
    r"<!DOCTYPE\b|</?(?:html|head|body|div|p|span|table|thead|tbody|tr|td|th|ul|ol|li|br|strong|em|h[1-6]|a|img|style|script)(?:\s+[^<>]*)?\s*/?>",
    re.IGNORECASE,
)
ID_PATTERN = re.compile(r"(?:公民身份号码|身份证(?:号码|号)?)[：: \t]*([0-9Xx]+)(?![0-9A-Za-z])")
USCC_PATTERN = re.compile(r"(?:统一社会信用代码|社会信用代码)[：: \t]*([0-9A-Za-z]+)(?![0-9A-Za-z])")
MOBILE_PATTERN = re.compile(r"(?:手机号码|手机号|联系电话|联系方式)[：: \t]*([0-9][0-9 \t\u3000-]{4,30})")
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
    "涉案一次": "“涉案”一词",
    "被答辩人成为": "“被答辩人”称谓",
}

AI_PHRASES = (
    "形成完整证据链",
    "资金闭环证据",
    "完整证据链",
    "进一步印证",
    "至关重要",
    "彻底落空",
    "逻辑闭环",
    "印证闭环",
    "铁证如山",
    "锁定事实",
    "证据链",
    "一揽子",
    "切断",
    "闭环",
    "焊死",
)
AI_PHRASE_PATTERN = re.compile("|".join(re.escape(phrase) for phrase in sorted(AI_PHRASES, key=len, reverse=True)))

ARTICLE_QUERY_PATTERN = re.compile(
    r"^第?([〇零一二三四五六七八九十百千万两\d０-９]{1,12})条?(?:之([〇零一二三四五六七八九十百千万两\d０-９]{1,6}))?$"
)
FULL_WIDTH_DIGIT_TABLE = str.maketrans("０１２３４５６７８９", "0123456789")


class ReviewError(Exception):
    def __init__(self, status, message, exit_code=INPUT_FAILED_EXIT):
        super().__init__(message)
        self.status = status
        self.message = message
        self.exit_code = exit_code


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
        except OSError:
            os.replace(temporary_path, path)
    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink(missing_ok=True)


def resolve_output_path(value, protected_paths):
    output_path = Path(value).resolve()
    output_key = os.path.normcase(str(output_path))
    for protected_path in protected_paths:
        if output_key == os.path.normcase(str(Path(protected_path).resolve())):
            raise ReviewError("input_failed", "输出路径不能覆盖输入文件", INPUT_FAILED_EXIT)
    if output_path.exists():
        raise ReviewError("input_failed", "输出文件已存在，请使用新的输出路径", INPUT_FAILED_EXIT)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if not output_path.parent.is_dir():
            raise OSError("输出父路径不是目录")
    except OSError as error:
        raise ReviewError("input_failed", "输出目录不可写或无效", INPUT_FAILED_EXIT) from error
    return output_path


def write_json(path, data):
    write_text_exact(path, json.dumps(data, ensure_ascii=False, indent=2))


def read_json(path):
    try:
        return json.loads(read_text_exact(path).lstrip("\ufeff"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReviewError("input_failed", f"无法读取 JSON: {path}", INPUT_FAILED_EXIT) from error


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
        full_prefix = text[match.start():match.start(1)]
        is_landline_allowed = ("联系电话" in full_prefix or "联系方式" in full_prefix)
        landline_match = re.match(r"0\d{2,3}[ \t\u3000-]?\d{7,8}(?!\d)", raw)
        if is_landline_allowed and landline_match:
            continue
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

    for match in AI_PHRASE_PATTERN.finditer(text):
        issues.append(make_issue("AI味问题", match.start(), match.end(), match.group(0),
                                 "检测到典型AI味套话或伪专业黑话，建议删除或改为客观事实陈述"))

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
        "ruleIssues": collect_rule_issues(text),
    }


def prepare_command(args):
    documents = []
    source_paths = [Path(value).resolve() for value in (args.files or [args.text_file])]
    if len(set(source_paths)) != len(source_paths):
        raise ReviewError("input_failed", "输入文件不能重复", INPUT_FAILED_EXIT)
    for source_path in source_paths:
        if not source_path.is_file():
            raise ReviewError("input_failed", f"输入文件不存在: {source_path}", INPUT_FAILED_EXIT)
        if source_path.stat().st_size == 0:
            raise ReviewError("input_failed", f"输入文件不能为空: {source_path}", INPUT_FAILED_EXIT)
    output_path = resolve_output_path(args.output, source_paths)
    for source_path in source_paths:
        text = read_text_exact(source_path)
        source = {
            "type": "text",
            "name": source_path.name,
            "path": str(source_path),
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        }
        documents.append(build_document_context(source, text))
    context = {
        "version": 3,
        "status": "ok",
        "documents": documents,
        "itemErrors": [],
    }
    write_json(output_path, context)
    return {
        "status": "ok",
        "output": str(output_path),
        "documents": len(documents),
        "itemErrors": 0,
        "ruleIssues": sum(len(item["ruleIssues"]) for item in documents),
    }


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


def docx_command(args):
    source_path = Path(args.input).resolve()
    if not source_path.is_file():
        raise ReviewError("input_failed", f"输入文本文件不存在: {source_path}", INPUT_FAILED_EXIT)
    text = read_text_exact(source_path)
    if not text.strip():
        raise ReviewError("input_failed", "文书正文不能为空", INPUT_FAILED_EXIT)
    output_path = resolve_output_path(args.output, [source_path])
    if output_path.suffix.lower() != ".docx":
        raise ReviewError("input_failed", "输出文件必须使用 .docx 后缀", INPUT_FAILED_EXIT)
    payload = {"text": text}
    if args.file_name:
        payload["fileName"] = args.file_name
    req = urllib.request.Request(
        DOCX_SERVICE_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8", "Accept": "*/*"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            content = resp.read()
    except Exception as error:
        raise ReviewError("request_failed", f"Word 导出接口请求失败: {error}", INPUT_FAILED_EXIT) from error
    try:
        with output_path.open("xb") as f:
            f.write(content)
    except Exception as error:
        raise ReviewError("input_failed", f"无法写入输出文件: {error}", INPUT_FAILED_EXIT) from error
    return {"status": "ok", "output": str(output_path), "bytes": len(content)}


def build_parser():
    parser = argparse.ArgumentParser(description="寻法本地法律文书检查与修订引擎（已移除登录及云端文件解析）")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="解析本地 UTF-8 文本并生成规则检查上下文")
    source_group = prepare.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--files", nargs="+", help="一个或多个本地 UTF-8 文本文件路径")
    source_group.add_argument("--text-file", help="单个本地 UTF-8 文本文件路径")
    prepare.add_argument("--output", required=True, help="检查上下文 JSON 输出路径")
    prepare.set_defaults(handler=prepare_command)

    apply_parser = subparsers.add_parser("apply", help="只替换确认错误并输出完整修正版")
    apply_parser.add_argument("--context", required=True, help="prepare 生成的检查上下文")
    apply_parser.add_argument("--document-number", required=True, type=int, help="要生成修正版的文书序号，从 1 开始")
    apply_parser.add_argument("--issues", required=True, help="确认修改的问题 JSON")
    apply_parser.add_argument("--output", required=True, help="修正版文本输出路径")
    apply_parser.set_defaults(handler=apply_command)

    docx_parser = subparsers.add_parser("docx", help="将法律文书纯文本通过接口生成标准 Word (DOCX)")
    docx_parser.add_argument("--input", required=True, help="纯文本 UTF-8 文件路径")
    docx_parser.add_argument("--file-name", help="下载文件名")
    docx_parser.add_argument("--output", required=True, help="新建 DOCX 输出路径")
    docx_parser.set_defaults(handler=docx_command)
    return parser


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = args.handler(args)
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
