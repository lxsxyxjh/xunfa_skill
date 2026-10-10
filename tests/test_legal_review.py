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

from legal_review import apply_command, collect_rule_issues


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


    def test_contact_phone_accepts_landline_and_mobile(self):
        text = (
            "原告：广东万佳建设有限公司，联系电话：0662-6500899。\n"
            "被告：阳江市江城区白沙街福岗村民委员会，联系电话：13078361130。"
        )
        issues = collect_rule_issues(text)
        self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()
