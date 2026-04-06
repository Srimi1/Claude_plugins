from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from eno.analyze import analyze_project
from eno.deploy import prepare_deploy_vercel
from eno.domain import connect_domain
from eno.validate import validate_go_live


class EnoIntegrationTests(unittest.TestCase):
    @patch("eno.deploy._git_status_clean", return_value=(True, ""))
    @patch("eno.validate._run_dig")
    def test_static_flow(self, mock_dig, _mock_git) -> None:
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
                json.dumps(
                    {
                        "dependencies": {"next": "14.2.0"},
                        "scripts": {"dev": "next dev"},
                    }
                )
            )

            analysis = analyze_project(str(project))
            deploy = prepare_deploy_vercel(str(project))
            validation = validate_go_live("example.com")

            self.assertIn(analysis.status, {"warn", "error"})
            self.assertEqual("warn", deploy.status)
            self.assertEqual("warn", validation.status)


if __name__ == "__main__":
    unittest.main()
