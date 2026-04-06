from __future__ import annotations

import argparse
import json

from .analyze import analyze_project
from .deploy import prepare_deploy_vercel
from .deploy_netlify import prepare_deploy_netlify
from .deploy_github_pages import prepare_deploy_github_pages
from .domain import connect_domain, SUPPORTED_PROVIDERS
from .guide import full_guide
from .validate import validate_go_live
from .vibe_advisor import vibe_coding_advisor

_ALL_PROVIDERS = sorted(SUPPORTED_PROVIDERS)


def _print(result) -> None:
    print(json.dumps(result.to_dict(), indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(prog="eno", description="Eno — vibe coding and deployment assistant")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("guide", help="Full end-to-end walkthrough: vibe code → deploy → domain → validate")

    sub.add_parser("vibe_advice", help="Phase-by-phase vibe coding guidance with prompt templates and quality gates")

    p_analyze = sub.add_parser("analyze_project", help="Analyze project type and detect deployment blockers")
    p_analyze.add_argument("project_path", help="Path to project directory")

    p_deploy_v = sub.add_parser("prepare_deploy_vercel", help="Prepare Vercel deployment plan")
    p_deploy_v.add_argument("project_path", help="Path to project directory")
    p_deploy_v.add_argument("--run-automation", action="store_true", help="Mark deploy sequence for automation")

    p_deploy_n = sub.add_parser("prepare_deploy_netlify", help="Prepare Netlify deployment plan")
    p_deploy_n.add_argument("project_path", help="Path to project directory")
    p_deploy_n.add_argument("--run-automation", action="store_true", help="Mark deploy sequence for automation")

    p_deploy_g = sub.add_parser("prepare_deploy_github_pages", help="Prepare GitHub Pages deployment plan (free, static/Vite/CRA)")
    p_deploy_g.add_argument("project_path", help="Path to project directory")
    p_deploy_g.add_argument("--repo-name", default="", help="GitHub repo in owner/repo format, e.g. alice/my-site")

    p_domain = sub.add_parser("connect_domain", help="Generate DNS record guidance for your registrar")
    p_domain.add_argument("domain", help="Root domain, e.g. example.com")
    p_domain.add_argument(
        "--provider",
        default="generic",
        choices=_ALL_PROVIDERS,
        help=f"DNS provider template. Supported: {', '.join(_ALL_PROVIDERS)}",
    )
    p_domain.add_argument("--needs-verification-txt", action="store_true", help="Include Vercel domain verification TXT record")
    p_domain.add_argument("--apex-target", default="76.76.21.21", help="Apex A record IP (default: Vercel)")
    p_domain.add_argument("--www-target", default="cname.vercel-dns.com", help="www CNAME hostname (default: Vercel)")

    p_validate = sub.add_parser("validate_go_live", help="Validate DNS and HTTPS readiness post-deployment")
    p_validate.add_argument("domain", help="Root domain")
    p_validate.add_argument("--expected-apex", default="76.76.21.21")
    p_validate.add_argument("--expected-www-cname", default="cname.vercel-dns.com")

    args = parser.parse_args()

    if args.command == "guide":
        _print(full_guide())
    elif args.command == "vibe_advice":
        _print(vibe_coding_advisor())
    elif args.command == "analyze_project":
        _print(analyze_project(args.project_path))
    elif args.command == "prepare_deploy_vercel":
        _print(prepare_deploy_vercel(args.project_path, run_automation=args.run_automation))
    elif args.command == "prepare_deploy_netlify":
        _print(prepare_deploy_netlify(args.project_path, run_automation=args.run_automation))
    elif args.command == "prepare_deploy_github_pages":
        _print(prepare_deploy_github_pages(args.project_path, repo_name=args.repo_name))
    elif args.command == "connect_domain":
        _print(
            connect_domain(
                args.domain,
                provider=args.provider,
                apex_target=args.apex_target,
                www_target=args.www_target,
                needs_verification_txt=args.needs_verification_txt,
            )
        )
    elif args.command == "validate_go_live":
        _print(
            validate_go_live(
                args.domain,
                expected_apex=args.expected_apex,
                expected_www_cname=args.expected_www_cname,
            )
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
