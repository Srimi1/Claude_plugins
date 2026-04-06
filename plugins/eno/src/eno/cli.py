from __future__ import annotations

import argparse
import json

from .analyze import analyze_project
from .deploy import prepare_deploy_vercel
from .domain import connect_domain
from .validate import validate_go_live
from .vibe_advisor import vibe_coding_advisor


def _print(result) -> None:
    print(json.dumps(result.to_dict(), indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(prog="eno", description="Eno Claude plugin assistant")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("vibe_advice", help="Get vibe-coding guidance")

    p_analyze = sub.add_parser("analyze_project", help="Analyze project readiness")
    p_analyze.add_argument("project_path", help="Path to project directory")

    p_deploy = sub.add_parser("prepare_deploy_vercel", help="Prepare Vercel deployment plan")
    p_deploy.add_argument("project_path", help="Path to project directory")
    p_deploy.add_argument("--run-automation", action="store_true", help="Mark deploy sequence for automation")

    p_domain = sub.add_parser("connect_domain", help="Generate domain connection guidance")
    p_domain.add_argument("domain", help="Root domain, e.g. example.com")
    p_domain.add_argument(
        "--provider",
        default="generic",
        choices=["generic", "cloudflare", "godaddy", "namecheap"],
        help="DNS provider template",
    )
    p_domain.add_argument("--needs-verification-txt", action="store_true")

    p_validate = sub.add_parser("validate_go_live", help="Validate go-live DNS readiness")
    p_validate.add_argument("domain", help="Root domain")
    p_validate.add_argument("--expected-apex", default="76.76.21.21")
    p_validate.add_argument("--expected-www-cname", default="cname.vercel-dns.com")

    args = parser.parse_args()

    if args.command == "vibe_advice":
        _print(vibe_coding_advisor())
    elif args.command == "analyze_project":
        _print(analyze_project(args.project_path))
    elif args.command == "prepare_deploy_vercel":
        _print(prepare_deploy_vercel(args.project_path, run_automation=args.run_automation))
    elif args.command == "connect_domain":
        _print(
            connect_domain(
                args.domain,
                provider=args.provider,
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
