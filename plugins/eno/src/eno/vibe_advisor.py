from __future__ import annotations

from .contracts import OperationResult, STATUS_OK


def vibe_coding_advisor() -> OperationResult:
    return OperationResult(
        status=STATUS_OK,
        findings=[
            "Vibe-coding works best when you lock a narrow page goal before writing prompts.",
            "Fast iteration requires a stable folder structure and a quick feedback loop.",
        ],
        actions=[
            "Define one user journey for this page in 3 sentences.",
            "Pick stack: static HTML/CSS/JS or Next.js (App Router).",
            "Create a quality gate: build passes, no console errors, and mobile layout review.",
            "Use short prompts that request one change at a time.",
        ],
        commands=[],
        next_steps=[
            "Run analyze_project to detect project type and deployment blockers.",
            "Use prepare_deploy_vercel before attempting domain connection.",
        ],
        meta={
            "prompt_templates": [
                "Create a hero section with one CTA, semantic HTML, and responsive CSS.",
                "Refactor this page to reduce CLS and improve mobile readability.",
                "Add analytics event hooks for primary CTA clicks.",
            ],
            "common_mistakes": [
                "Changing multiple concerns in one prompt, making regressions harder to isolate.",
                "Skipping production build checks before deployment.",
                "Ignoring environment variables for API-backed pages.",
            ],
        },
    )
