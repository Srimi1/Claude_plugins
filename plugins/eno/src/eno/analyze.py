from __future__ import annotations

import json
import os
from pathlib import Path

from .contracts import OperationResult, STATUS_ERROR, STATUS_OK, STATUS_WARN


def _read_package_json(project_path: Path) -> dict:
    package_json = project_path / "package.json"
    if not package_json.exists():
        return {}
    try:
        return json.loads(package_json.read_text())
    except json.JSONDecodeError:
        return {"_invalid": True}


def detect_project_type(project_path: str) -> str:
    path = Path(project_path)
    pkg = _read_package_json(path)

    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

    if deps.get("next") or (path / "next.config.js").exists() or (path / "next.config.mjs").exists():
        return "nextjs"

    if deps.get("@sveltejs/kit") or (path / "svelte.config.js").exists() or (path / "svelte.config.ts").exists():
        return "sveltekit"

    if deps.get("react-scripts"):
        return "cra"

    if deps.get("vite") or (path / "vite.config.js").exists() or (path / "vite.config.ts").exists():
        return "vite"

    static_markers = ["index.html", "public/index.html"]
    if any((path / marker).exists() for marker in static_markers):
        return "static"

    return "unknown"


def analyze_project(project_path: str) -> OperationResult:
    path = Path(project_path)
    if not path.exists() or not path.is_dir():
        return OperationResult(
            status=STATUS_ERROR,
            findings=[f"Project path does not exist or is not a directory: {project_path}"],
            actions=["Provide a valid project directory path."],
            commands=[],
            next_steps=["Re-run analyze_project with a valid local path."],
            meta={"project_type": "unknown"},
        )

    project_type = detect_project_type(project_path)
    pkg = _read_package_json(path)

    findings: list[str] = []
    actions: list[str] = []
    status = STATUS_OK

    type_messages = {
        "nextjs": "Detected Next.js project. Build output: .next/ — deploy via Vercel or Netlify.",
        "sveltekit": "Detected SvelteKit project. Build output depends on adapter (default: build/).",
        "cra": "Detected Create React App project. Build output: build/ — deploy via Netlify or GitHub Pages.",
        "vite": "Detected Vite project. Build output: dist/ — deploy via Netlify, Vercel, or GitHub Pages.",
        "static": "Detected static website project. Deploy root directory or public/ folder.",
    }
    if project_type in type_messages:
        findings.append(type_messages[project_type])
    else:
        status = STATUS_WARN
        findings.append("Could not confidently detect project type (expected static, Vite, CRA, SvelteKit, or Next.js).")
        actions.append("Add package.json and/or index.html so Eno can infer deployment path.")

    if pkg.get("_invalid"):
        status = STATUS_ERROR
        findings.append("package.json is present but invalid JSON.")
        actions.append("Fix JSON syntax in package.json before deployment checks.")
    elif pkg:
        scripts = pkg.get("scripts", {})
        if "build" not in scripts:
            if status != STATUS_ERROR:
                status = STATUS_WARN
            findings.append("No build script found in package.json.")
            actions.append("Add a build script (for example: next build).")
        if "start" not in scripts and project_type in ("nextjs", "cra"):
            findings.append("No start script found; deployment platforms can still deploy, but local validation may be limited.")

    env_files = [".env", ".env.local", ".env.production"]
    found_env = [name for name in env_files if (path / name).exists()]
    if found_env:
        findings.append(f"Environment files detected: {', '.join(found_env)}")
        actions.append("Ensure required secrets are configured in Vercel project settings.")

    next_steps = [
        "Run vibe_advice for structured vibe-coding guidance.",
        "Run prepare_deploy_vercel to generate deploy-ready commands and checks.",
    ]

    return OperationResult(
        status=status,
        findings=findings,
        actions=actions,
        commands=[],
        next_steps=next_steps,
        meta={
            "project_type": project_type,
            "absolute_path": os.path.abspath(project_path),
        },
    )
