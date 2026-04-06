from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .analyze import detect_project_type
from .contracts import OperationResult, STATUS_ERROR, STATUS_OK, STATUS_WARN

# Build output directory per project type
_BUILD_DIR = {
    "vite": "dist",
    "cra": "build",
    "sveltekit": "build",
    "nextjs": ".next",
    "static": ".",
    "unknown": ".",
}


def _read_package_json(project_path: Path) -> dict:
    package_json = project_path / "package.json"
    if not package_json.exists():
        return {}
    try:
        return json.loads(package_json.read_text())
    except json.JSONDecodeError:
        return {"_invalid": True}


def _git_status_clean(project_path: Path) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_path,
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            return False, "Git status could not be checked."
        return proc.stdout.strip() == "", "Repository has uncommitted changes." if proc.stdout.strip() else ""
    except FileNotFoundError:
        return False, "Git is not available in PATH."


def prepare_deploy_netlify(project_path: str, run_automation: bool = False) -> OperationResult:
    path = Path(project_path)
    if not path.exists() or not path.is_dir():
        return OperationResult(
            status=STATUS_ERROR,
            findings=[f"Project path does not exist: {project_path}"],
            actions=["Use a valid local project path."],
            commands=[],
            next_steps=["Re-run prepare_deploy_netlify with an existing project directory."],
        )

    project_type = detect_project_type(project_path)
    pkg = _read_package_json(path)
    deploy_dir = _BUILD_DIR.get(project_type, ".")

    status = STATUS_OK
    findings: list[str] = []
    actions: list[str] = []
    commands: list[str] = []

    if project_type == "unknown":
        status = STATUS_WARN
        findings.append("Project type is unknown; deployment steps may be incomplete.")
        actions.append("Add static marker files or framework config so Eno can detect the type.")
    else:
        findings.append(f"Preparing Netlify deployment for {project_type} project.")
        findings.append(f"Deploy directory: {deploy_dir}/")

    if pkg.get("_invalid"):
        status = STATUS_ERROR
        findings.append("package.json has invalid JSON.")
        actions.append("Fix package.json before deployment.")

    if pkg:
        scripts = pkg.get("scripts", {})
        if "build" not in scripts:
            if status != STATUS_ERROR:
                status = STATUS_WARN
            findings.append("No build script found in package.json.")
            actions.append("Add build script so Netlify can build your project automatically.")

    is_clean, reason = _git_status_clean(path)
    if not is_clean:
        if status == STATUS_OK:
            status = STATUS_WARN
        findings.append(f"Git readiness warning: {reason}")
        actions.append("Commit or stash local changes before production deployment.")
    else:
        findings.append("Git working tree is clean.")

    if project_type == "static":
        commands.extend([
            "npx netlify login",
            "npx netlify deploy --dir=.",
            "npx netlify deploy --prod --dir=.",
        ])
    else:
        commands.extend([
            "npm install",
            "npm run build",
            "npx netlify login",
            f"npx netlify deploy --dir={deploy_dir}",
            f"npx netlify deploy --prod --dir={deploy_dir}",
        ])

    if run_automation and status != STATUS_ERROR:
        actions.append("Automation enabled: execute build and Netlify commands in sequence.")

    next_steps = [
        "Deploy project on Netlify using listed commands.",
        f"In Netlify dashboard, set publish directory to '{deploy_dir}'.",
        "Run connect_domain with your root domain and preferred DNS provider.",
        "Run validate_go_live after DNS updates propagate.",
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
            "run_automation": run_automation,
            "platform": "netlify",
        },
    )
