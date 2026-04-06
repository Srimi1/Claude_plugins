from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from eno.analyze import analyze_project, detect_project_type
from eno.contracts import REQUIRED_OUTPUT_FIELDS, validate_result_shape
from eno.deploy import prepare_deploy_vercel
from eno.domain import connect_domain
from eno.validate import validate_go_live
from eno.vibe_advisor import vibe_coding_advisor


class EnoTests(unittest.TestCase):
    def _assert_contract(self, result) -> None:
        payload = result.to_dict()
        missing = validate_result_shape(payload)
        self.assertEqual([], missing)
        self.assertTrue(REQUIRED_OUTPUT_FIELDS.issubset(set(payload.keys())))

    def test_detect_project_type_nextjs(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "package.json").write_text(
                json.dumps(
                    {
                        "dependencies": {"next": "14.2.0"},
                        "scripts": {"build": "next build"},
                    }
                )
            )
            self.assertEqual("nextjs", detect_project_type(str(path)))

    def test_detect_project_type_static(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "index.html").write_text("<html></html>")
            self.assertEqual("static", detect_project_type(str(path)))

    def test_analyze_project_missing_build(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "package.json").write_text(
                json.dumps(
                    {
                        "dependencies": {"next": "14.2.0"},
                        "scripts": {"dev": "next dev"},
                    }
                )
            )
            result = analyze_project(str(path))
            self._assert_contract(result)
            self.assertIn(result.status, {"warn", "error"})
            self.assertTrue(any("build script" in finding.lower() for finding in result.findings))

    @patch("eno.deploy._git_status_clean", return_value=(True, ""))
    def test_prepare_deploy_vercel_nextjs(self, _mock_git) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "package.json").write_text(
                json.dumps(
                    {
                        "dependencies": {"next": "14.2.0"},
                        "scripts": {"build": "next build", "start": "next start"},
                    }
                )
            )
            result = prepare_deploy_vercel(str(path), run_automation=True)
            self._assert_contract(result)
            self.assertEqual("nextjs", result.meta["project_type"])
            self.assertTrue(any("vercel" in command.lower() for command in result.commands))

    def test_connect_domain_cloudflare(self) -> None:
        result = connect_domain("example.com", provider="cloudflare", needs_verification_txt=True)
        self._assert_contract(result)
        records = result.meta["records"]
        types = {record["type"] for record in records}
        self.assertIn("A", types)
        self.assertIn("CNAME", types)
        self.assertIn("TXT", types)

    def test_connect_domain_unknown_provider(self) -> None:
        result = connect_domain("example.com", provider="unknown-provider")
        self._assert_contract(result)
        self.assertEqual("warn", result.status)
        self.assertEqual("generic", result.meta["provider"])

    @patch("eno.validate._run_dig")
    def test_validate_go_live_success(self, mock_dig) -> None:
        def side_effect(record_type: str, host: str) -> list[str]:
            if record_type == "A":
                return ["76.76.21.21"]
            return ["cname.vercel-dns.com"]

        mock_dig.side_effect = side_effect
        result = validate_go_live("example.com")
        self._assert_contract(result)
        self.assertEqual("ok", result.status)

    @patch("eno.validate._run_dig", return_value=[])
    def test_validate_go_live_no_dns_data(self, _mock_dig) -> None:
        result = validate_go_live("example.com")
        self._assert_contract(result)
        self.assertEqual("warn", result.status)

    def test_vibe_advice_contract(self) -> None:
        result = vibe_coding_advisor()
        self._assert_contract(result)
        self.assertGreater(len(result.meta.get("prompt_templates", [])), 0)


if __name__ == "__main__":
    unittest.main()
