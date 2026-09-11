import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SCRIPTS_DIRECTORY = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIRECTORY))

from legal_review import XunfaClient, apply_command, auth_qr_wait_command


class SseResponse:
    headers = {"Content-Type": "text/event-stream;charset=UTF-8"}

    def __init__(self, lines):
        self.lines = lines

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        return False

    def __iter__(self):
        return iter(self.lines)


class ApplyCommandTests(unittest.TestCase):
    def test_confirmed_ai_issues_only_change_selected_ranges(self):
        text = (
            "双方借贷合意真实合法，内容清晰明确：原、被告自愿达成口头借款约定。\n"
            "该转账进一步印证被告已实际收款。\n"
            "依据《中华人民共和国民法典》第一千一百六十五条主张权利。"
        )
        summary = "双方借贷合意真实合法，内容清晰明确："
        phrase = "进一步印证"
        citation = "《中华人民共和国民法典》第一千一百六十五条"
        text_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context_path = root / "review-context.json"
            issues_path = root / "accepted-issues.json"
            output_path = root / "corrected.txt"
            context_path.write_text(json.dumps({
                "documents": [{
                    "source": {"type": "text"},
                    "text": text,
                    "textSha256": text_sha256,
                }],
            }, ensure_ascii=False), encoding="utf-8")
            issues_path.write_text(json.dumps({
                "textSha256": text_sha256,
                "issues": [
                    {
                        "category": "AI味问题",
                        "apply": True,
                        "replacementStatus": "ready",
                        "start": 0,
                        "end": len(summary),
                        "original": summary,
                        "replacement": "",
                    },
                    {
                        "category": "AI味问题",
                        "apply": True,
                        "replacementStatus": "ready",
                        "start": text.index(phrase),
                        "end": text.index(phrase) + len(phrase),
                        "original": phrase,
                        "replacement": "印证",
                    },
                ],
            }, ensure_ascii=False), encoding="utf-8")

            result = apply_command(SimpleNamespace(
                context=str(context_path),
                document_number=1,
                issues=str(issues_path),
                output=str(output_path),
            ))

            self.assertEqual(result["applied"], 2)
            corrected = output_path.read_text(encoding="utf-8")
            self.assertIn(citation, corrected)
            self.assertEqual(corrected, (
                "原、被告自愿达成口头借款约定。\n"
                "该转账印证被告已实际收款。\n"
                "依据《中华人民共和国民法典》第一千一百六十五条主张权利。"
            ))


class AuthQrWaitCommandTests(unittest.TestCase):
    def test_sse_event_exchanges_login_cookie_once(self):
        def check_login(client, path, values):
            self.assertEqual(path, "/checkWXLogin")
            self.assertEqual(values, {"uuid": "qr-uuid"})
            return {"code": 1, "data": {"userna": "wx-user"}}

        with patch("legal_review.urllib.request.urlopen", return_value=SseResponse((
                    b"event: wx-login-completed\n", b"data: completed\n", b"\n"))) as urlopen, \
                patch.object(XunfaClient, "send_form", autospec=True, side_effect=check_login) as send_form, \
                patch("legal_review.extract_cookie_token", return_value="login-token"), \
                patch("legal_review.save_auth") as save_auth:
            result = auth_qr_wait_command(SimpleNamespace(uuid="qr-uuid", timeout=5, base_url="http://127.0.0.1"))

        self.assertEqual(result, {"status": "ok", "username": "wx-user"})
        self.assertEqual(urlopen.call_count, 1)
        self.assertEqual(send_form.call_count, 1)
        save_auth.assert_called_once_with("http://127.0.0.1", "login-token", "wx-user")

    def test_sse_reconnects_without_repeating_login_exchange(self):
        def check_login(client, path, values):
            self.assertEqual(path, "/checkWXLogin")
            self.assertEqual(values, {"uuid": "qr-uuid"})
            return {"code": 1, "data": {"userna": "wx-user"}}

        with patch("legal_review.urllib.request.urlopen", side_effect=(
                    SseResponse(()), SseResponse((b"event: wx-login-completed\n", b"\n")))) as urlopen, \
                patch("legal_review.time.sleep"), \
                patch.object(XunfaClient, "send_form", autospec=True, side_effect=check_login) as send_form, \
                patch("legal_review.extract_cookie_token", return_value="login-token"), \
                patch("legal_review.save_auth"):
            auth_qr_wait_command(SimpleNamespace(uuid="qr-uuid", timeout=5, base_url="http://127.0.0.1"))

        self.assertEqual(urlopen.call_count, 2)
        self.assertEqual(send_form.call_count, 1)


if __name__ == "__main__":
    unittest.main()
