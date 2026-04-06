from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from eno.analyze import analyze_project
from eno.deploy import prepare_deploy_vercel
from eno.deploy_netlify import prepare_deploy_netlify
from eno.deploy_github_pages import prepare_deploy_github_pages
from eno.domain import connect_domain
from eno.guide import full_guide
from eno.validate import validate_go_live
from eno.vibe_advisor import vibe_coding_advisor


class EnoIntegrationTests(unittest.TestCase):

    @patch("eno.deploy._git_status_clean", return_value=(True, ""))
    @patch("eno.validate._run_dig")
    def test_static_site_vercel_flow(self, mock_dig, _mock_git) -> None:
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            (project / "index.html").write_text("<html><body>hello</body></html>")

            analysis = analyze_project(str(project))
            deploy = prepare_deploy_vercel(str(project))
            domain = connect_domain("example.com", provider="godaddy")

            mock_dig.side_effect = lambda record_type, host: (
                ["76.76.21.21"] if record_type == "A" else ["cname.vercel-dns.com"]
            )
            validation = validate_go_live("example.com")

            self.assertEqual("static", analysis.meta["project_type"])
            self.assertIn(deploy.status, {"ok", "warn"})
            self.assertEqual("godaddy", domain.meta["provider"])
            self.assertEqual("ok", validation.status)

    @patch("eno.deploy._git_status_clean", return_value=(False, "Repository has uncommitted changes."))
    @patch("eno.validate._run_dig", return_value=[])
    def test_nextjs_failure_paths(self, _mock_dig, _mock_git) -> None:
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            (project / "package.json").write_text(
                json.dumps({"dependencies": {"next": "14.2.0"}, "scripts": {"dev": "next dev"}})
            )

            analysis = analyze_project(str(project))
            deploy = prepare_deploy_vercel(str(project))
            validation = validate_go_live("example.com")

            self.assertIn(analysis.status, {"warn", "error"})
            self.assertEqual("warn", deploy.status)
            self.assertEqual("warn", validation.status)

    @patch("eno.deploy_netlify._git_status_clean", return_value=(True, ""))
    @patch("eno.validate._run_dig")
    def test_vite_netlify_flow(self, mock_dig, _mock_git) -> None:
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            (project / "vite.config.js").write_text("export default {}")
            (project / "package.json").write_text(
                json.dumps({"devDependencies": {"vite": "^5.0.0"}, "scripts": {"build": "vite build"}})
            )

            analysis = analyze_project(str(project))
            deploy = prepare_deploy_netlify(str(project))
            domain = connect_domain("example.com", provider="porkbun")

            mock_dig.side_effect = lambda record_type, host: (
                ["76.76.21.21"] if record_type == "A" else ["cname.vercel-dns.com"]
            )
            validation = validate_go_live("example.com")

            self.assertEqual("vite", analysis.meta["project_type"])
            self.assertEqual("ok", deploy.status)
            self.assertEqual("dist", deploy.meta["deploy_dir"])
            self.assertEqual("porkbun", domain.meta["provider"])
            self.assertEqual("ok", validation.status)

    def test_static_github_pages_flow(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            (project / "index.html").write_text("<html><body>hello</body></html>")

            analysis = analyze_project(str(project))
            deploy = prepare_deploy_github_pages(str(project), repo_name="alice/my-site")
            domain = connect_domain("example.com", provider="namecheap")

            self.assertEqual("static", analysis.meta["project_type"])
            self.assertIn(deploy.status, {"ok", "warn"})
            self.assertEqual("github_pages", deploy.meta["platform"])
            self.assertEqual("namecheap", domain.meta["provider"])

    def test_vibe_to_guide_flow(self) -> None:
        advice = vibe_coding_advisor()
        guide = full_guide()

        self.assertEqual("ok", advice.status)
        self.assertEqual("ok", guide.status)
        self.assertGreater(len(advice.meta.get("phases", [])), 0)
        self.assertIn("vercel", guide.meta.get("platform_guide", {}))
        self.assertIn("netlify", guide.meta.get("platform_guide", {}))
        self.assertIn("github_pages", guide.meta.get("platform_guide", {}))


if __name__ == "__main__":
    unittest.main()
