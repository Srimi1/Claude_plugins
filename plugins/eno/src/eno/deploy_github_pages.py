from __future__ import annotations

import json
from pathlib import Path

from .analyze import detect_project_type
from .contracts import OperationResult, STATUS_ERROR, STATUS_OK, STATUS_WARN

# Build output directory per project type for GitHub Pages
_BUILD_DIR = {
    "vite": "dist",
    "cra": "build",
    "sveltekit": "build",
    "static": ".",
    "unknown": ".",
}

# Project types NOT well-suited for GitHub Pages (no server-side rendering)
_UNSUPPORTED_TYPES = {"nextjs"}


def _read_package_json(project_path: Path) -> dict:
    package_json = project_path / "package.json"
    if not package_json.exists():
        return {}
    try:
        return json.loads(package_json.read_text())
    except json.JSONDecodeError:
        return {"_invalid": True}


def prepare_deploy_github_pages(project_path: str, repo_name: str = "") -> OperationResult:
    path = Path(project_path)
    if not path.exists() or not path.is_dir():
        return OperationResult(
            status=STATUS_ERROR,
            findings=[f"Project path does not exist: {project_path}"],
            actions=["Use a valid local project path."],
            commands=[],
            next_steps=["Re-run prepare_deploy_github_pages with an existing project directory."],
        )

    project_type = detect_project_type(project_path)
    pkg = _read_package_json(path)

    status = STATUS_OK
    findings: list[str] = []
    actions: list[str] = []
    commands: list[str] = []

    if project_type in _UNSUPPORTED_TYPES:
        status = STATUS_WARN
        findings.append(
            f"Project type '{project_type}' uses server-side rendering and is not well-suited for GitHub Pages."
        )
        actions.append("Consider Vercel or Netlify instead, which support SSR natively.")
        actions.append("If you only need static export, add 'output: export' to next.config.js and treat output as static.")

    deploy_dir = _BUILD_DIR.get(project_type, ".")
    findings.append(f"Preparing GitHub Pages deployment for {project_type} project.")
    findings.append(f"Deploy directory: {deploy_dir}/")
    findings.append("GitHub Pages is free and requires no account beyond GitHub.")

    if pkg.get("_invalid"):
        status = STATUS_ERROR
        findings.append("package.json has invalid JSON.")
        actions.append("Fix package.json before deployment.")

    if pkg and project_type not in ("static",):
        scripts = pkg.get("scripts", {})
        if "build" not in scripts:
            if status != STATUS_ERROR:
                status = STATUS_WARN
            findings.append("No build script found in package.json.")
            actions.append("Add a build script (e.g. 'vite build' or 'react-scripts build').")

    pages_url = f"https://<username>.github.io/{repo_name.split('/')[-1] if repo_name else '<repo>'}"

    if project_type == "static":
        commands.extend([
            "git add . && git commit -m 'deploy: update static site'",
            "git push origin main",
        ])
        actions.append("In GitHub repo Settings -> Pages, set Source = Deploy from branch, Branch = main, Folder = / (root).")
    elif project_type in ("vite", "cra", "sveltekit"):
        pkg_name = pkg.get("name", "my-app") if pkg else "my-app"
        commands.extend([
            "npm install",
            "npm install --save-dev gh-pages",
            "npm run build",
            f'npx gh-pages -d {deploy_dir}',
        ])
        actions.append(f"Add 'homepage': '{pages_url}' to package.json.")
        actions.append("Add 'predeploy': 'npm run build' and 'deploy': 'gh-pages -d " + deploy_dir + "' to package.json scripts.")
        actions.append("In GitHub repo Settings -> Pages, set Source = Deploy from branch, Branch = gh-pages.")
    else:
        commands.extend([
            "npm install",
            "npm run build",
            f"npx gh-pages -d {deploy_dir}",
        ])
        actions.append("In GitHub repo Settings -> Pages, set Source = Deploy from branch, Branch = gh-pages.")

    next_steps = [
        "Push your project to a GitHub repository if not done already.",
        "Enable GitHub Pages in repo Settings -> Pages.",
        f"Your site will be live at: {pages_url}",
        "For a custom domain, add a CNAME file in your repo root containing just your domain.",
        "Run connect_domain with --provider generic (or your DNS provider) after custom domain is set.",
    ]

    return OperationResult(
        status=status,
        findings=findings,
        actions=actions,
        commands=commands,
        next_steps=next_steps,
        meta={
            "project_type": project_type,
            "deploy_dir": deploy_dir,
            "repo_name": repo_name,
            "pages_url": pages_url,
            "platform": "github_pages",
        },
    )
