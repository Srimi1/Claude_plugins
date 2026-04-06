from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from eno.analyze import analyze_project, detect_project_type
from eno.contracts import REQUIRED_OUTPUT_FIELDS, validate_result_shape
from eno.deploy import prepare_deploy_vercel
from eno.deploy_netlify import prepare_deploy_netlify
from eno.deploy_github_pages import prepare_deploy_github_pages
from eno.domain import connect_domain
from eno.guide import full_guide
from eno.validate import validate_go_live
from eno.vibe_advisor import vibe_coding_advisor


class EnoTests(unittest.TestCase):
    def _assert_contract(self, result) -> None:
        payload = result.to_dict()
        missing = validate_result_shape(payload)
        self.assertEqual([], missing)
        self.assertTrue(REQUIRED_OUTPUT_FIELDS.issubset(set(payload.keys())))

    # --- detect_project_type ---

    def test_detect_project_type_nextjs(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "package.json").write_text(
                json.dumps({"dependencies": {"next": "14.2.0"}, "scripts": {"build": "next build"}})
            )
            self.assertEqual("nextjs", detect_project_type(str(path)))

    def test_detect_project_type_static(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "index.html").write_text("<html></html>")
            self.assertEqual("static", detect_project_type(str(path)))

    def test_detect_project_type_vite(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "vite.config.js").write_text("export default {}")
            self.assertEqual("vite", detect_project_type(str(path)))

    def test_detect_project_type_vite_via_deps(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "package.json").write_text(
                json.dumps({"devDependencies": {"vite": "^5.0.0"}})
            )
            self.assertEqual("vite", detect_project_type(str(path)))

    def test_detect_project_type_cra(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "package.json").write_text(
                json.dumps({"dependencies": {"react-scripts": "5.0.1"}})
            )
            self.assertEqual("cra", detect_project_type(str(path)))

    def test_detect_project_type_sveltekit(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "svelte.config.js").write_text("export default {}")
            self.assertEqual("sveltekit", detect_project_type(str(path)))

    # --- analyze_project ---

    def test_analyze_project_missing_build(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "package.json").write_text(
                json.dumps({"dependencies": {"next": "14.2.0"}, "scripts": {"dev": "next dev"}})
            )
            result = analyze_project(str(path))
            self._assert_contract(result)
            self.assertIn(result.status, {"warn", "error"})
            self.assertTrue(any("build script" in finding.lower() for finding in result.findings))

    def test_analyze_project_vite(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "vite.config.ts").write_text("export default {}")
            result = analyze_project(str(path))
            self._assert_contract(result)
            self.assertEqual("vite", result.meta["project_type"])

    # --- prepare_deploy_vercel ---

    @patch("eno.deploy._git_status_clean", return_value=(True, ""))
    def test_prepare_deploy_vercel_nextjs(self, _mock_git) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "package.json").write_text(
                json.dumps({"dependencies": {"next": "14.2.0"}, "scripts": {"build": "next build", "start": "next start"}})
            )
            result = prepare_deploy_vercel(str(path), run_automation=True)
            self._assert_contract(result)
            self.assertEqual("nextjs", result.meta["project_type"])
            self.assertTrue(any("vercel" in command.lower() for command in result.commands))

    # --- prepare_deploy_netlify ---

    @patch("eno.deploy_netlify._git_status_clean", return_value=(True, ""))
    def test_prepare_deploy_netlify_vite(self, _mock_git) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "vite.config.js").write_text("export default {}")
            (path / "package.json").write_text(
                json.dumps({"devDependencies": {"vite": "^5.0.0"}, "scripts": {"build": "vite build"}})
            )
            result = prepare_deploy_netlify(str(path))
            self._assert_contract(result)
            self.assertEqual("vite", result.meta["project_type"])
            self.assertEqual("dist", result.meta["deploy_dir"])
            self.assertTrue(any("netlify" in command.lower() for command in result.commands))

    @patch("eno.deploy_netlify._git_status_clean", return_value=(True, ""))
    def test_prepare_deploy_netlify_static(self, _mock_git) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "index.html").write_text("<html></html>")
            result = prepare_deploy_netlify(str(path))
            self._assert_contract(result)
            self.assertEqual("static", result.meta["project_type"])
            self.assertEqual(".", result.meta["deploy_dir"])

    def test_prepare_deploy_netlify_invalid_path(self) -> None:
        result = prepare_deploy_netlify("/nonexistent/path")
        self._assert_contract(result)
        self.assertEqual("error", result.status)

    # --- prepare_deploy_github_pages ---

    def test_prepare_deploy_github_pages_static(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "index.html").write_text("<html></html>")
            result = prepare_deploy_github_pages(str(path), repo_name="alice/my-site")
            self._assert_contract(result)
            self.assertEqual("static", result.meta["project_type"])
            self.assertEqual(".", result.meta["deploy_dir"])
            self.assertEqual("github_pages", result.meta["platform"])

    def test_prepare_deploy_github_pages_vite(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "vite.config.js").write_text("export default {}")
            (path / "package.json").write_text(
                json.dumps({"devDependencies": {"vite": "^5.0.0"}, "scripts": {"build": "vite build"}})
            )
            result = prepare_deploy_github_pages(str(path), repo_name="alice/my-site")
            self._assert_contract(result)
            self.assertEqual("dist", result.meta["deploy_dir"])
            self.assertTrue(any("gh-pages" in command for command in result.commands))

    def test_prepare_deploy_github_pages_nextjs_warns(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "package.json").write_text(
                json.dumps({"dependencies": {"next": "14.2.0"}, "scripts": {"build": "next build"}})
            )
            result = prepare_deploy_github_pages(str(path))
            self._assert_contract(result)
            self.assertEqual("warn", result.status)

    def test_prepare_deploy_github_pages_invalid_path(self) -> None:
        result = prepare_deploy_github_pages("/nonexistent/path")
        self._assert_contract(result)
        self.assertEqual("error", result.status)

    # --- connect_domain ---

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

    def test_connect_domain_porkbun(self) -> None:
        result = connect_domain("example.com", provider="porkbun")
        self._assert_contract(result)
        self.assertEqual("ok", result.status)
        self.assertEqual("porkbun", result.meta["provider"])
        self.assertTrue(len(result.actions) > 0)

    def test_connect_domain_squarespace(self) -> None:
        result = connect_domain("example.com", provider="squarespace")
        self._assert_contract(result)
        self.assertEqual("squarespace", result.meta["provider"])

    def test_connect_domain_route53(self) -> None:
        result = connect_domain("example.com", provider="route53")
        self._assert_contract(result)
        self.assertEqual("route53", result.meta["provider"])

    # --- validate_go_live ---

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

    # --- vibe_advisor ---

    def test_vibe_advice_contract(self) -> None:
        result = vibe_coding_advisor()
        self._assert_contract(result)
        self.assertGreater(len(result.meta.get("prompt_templates", [])), 0)

    def test_vibe_advice_has_phases(self) -> None:
        result = vibe_coding_advisor()
        phases = result.meta.get("phases", [])
        self.assertEqual(5, len(phases))

    def test_vibe_advice_has_quality_gate(self) -> None:
        result = vibe_coding_advisor()
        checklist = result.meta.get("quality_gate_checklist", [])
        self.assertGreater(len(checklist), 0)

    def test_vibe_advice_has_common_mistakes(self) -> None:
        result = vibe_coding_advisor()
        mistakes = result.meta.get("common_mistakes", [])
        self.assertGreater(len(mistakes), 0)

    # --- guide ---

    def test_guide_contract(self) -> None:
        result = full_guide()
        self._assert_contract(result)
        self.assertEqual("ok", result.status)

    def test_guide_has_platform_guide(self) -> None:
        result = full_guide()
        platform_guide = result.meta.get("platform_guide", {})
        self.assertIn("vercel", platform_guide)
        self.assertIn("netlify", platform_guide)
        self.assertIn("github_pages", platform_guide)

    def test_guide_has_full_workflow(self) -> None:
        result = full_guide()
        workflow = result.meta.get("full_workflow", [])
        self.assertGreaterEqual(len(workflow), 5)


if __name__ == "__main__":
    unittest.main()
