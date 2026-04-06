"""Eno MCP Server — exposes Eno capabilities as Claude tools.

Supports two transports:
  stdio (default)  — for Claude Code CLI / desktop
      python mcp_server.py

  http             — for Claude.ai web (Integrations → Custom plugin)
      python mcp_server.py --http [--port 8000]
"""
from __future__ import annotations

import argparse
import sys
import os

# Allow running directly without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mcp.server.fastmcp import FastMCP

from eno.analyze import analyze_project as _analyze_project
from eno.deploy import prepare_deploy_vercel as _prepare_deploy_vercel
from eno.deploy_netlify import prepare_deploy_netlify as _prepare_deploy_netlify
from eno.deploy_github_pages import prepare_deploy_github_pages as _prepare_deploy_github_pages
from eno.domain import connect_domain as _connect_domain
from eno.guide import full_guide as _full_guide
from eno.validate import validate_go_live as _validate_go_live
from eno.vibe_advisor import vibe_coding_advisor as _vibe_coding_advisor

mcp = FastMCP("Eno")


@mcp.tool()
def guide() -> dict:
    """Get a complete end-to-end walkthrough: vibe code → analyze → deploy → connect domain → validate."""
    return _full_guide().to_dict()


@mcp.tool()
def vibe_coding_advisor() -> dict:
    """Get phase-by-phase vibe coding guidance with prompt templates, quality gate checklist, stack guide, and common mistakes with fixes."""
    return _vibe_coding_advisor().to_dict()


@mcp.tool()
def analyze_project(project_path: str) -> dict:
    """Detect project type (static, Vite, CRA, SvelteKit, Next.js) and report any deployment blockers.

    Args:
        project_path: Absolute or relative path to the project directory.
    """
    return _analyze_project(project_path).to_dict()


@mcp.tool()
def prepare_deploy_vercel(project_path: str, run_automation: bool = False) -> dict:
    """Generate a Vercel deployment checklist and commands. Best for Next.js and SSR projects.

    Args:
        project_path: Absolute or relative path to the project directory.
        run_automation: When True, marks the deploy sequence for automated execution.
    """
    return _prepare_deploy_vercel(project_path, run_automation=run_automation).to_dict()


@mcp.tool()
def prepare_deploy_netlify(project_path: str, run_automation: bool = False) -> dict:
    """Generate a Netlify deployment checklist and commands. Detects build output dir per project type.

    Args:
        project_path: Absolute or relative path to the project directory.
        run_automation: When True, marks the deploy sequence for automated execution.
    """
    return _prepare_deploy_netlify(project_path, run_automation=run_automation).to_dict()


@mcp.tool()
def prepare_deploy_github_pages(project_path: str, repo_name: str = "") -> dict:
    """Generate a GitHub Pages deployment plan (free hosting). Warns on SSR projects like Next.js.

    Args:
        project_path: Absolute or relative path to the project directory.
        repo_name: GitHub repo in owner/repo format, e.g. alice/my-site (used to generate the live URL).
    """
    return _prepare_deploy_github_pages(project_path, repo_name=repo_name).to_dict()


@mcp.tool()
def connect_domain(
    domain: str,
    provider: str = "generic",
    apex_target: str = "76.76.21.21",
    www_target: str = "cname.vercel-dns.com",
    needs_verification_txt: bool = False,
) -> dict:
    """Generate DNS records and step-by-step instructions to connect a custom domain.

    Args:
        domain: Root domain to connect, e.g. example.com
        provider: DNS provider — one of: generic, cloudflare, godaddy, namecheap, porkbun, squarespace, route53
        apex_target: A record IP for the apex domain (default: Vercel's IP 76.76.21.21).
        www_target: CNAME target for www (default: cname.vercel-dns.com).
        needs_verification_txt: Set True if your deployment platform requires a TXT ownership verification record.
    """
    return _connect_domain(
        domain,
        provider=provider,
        apex_target=apex_target,
        www_target=www_target,
        needs_verification_txt=needs_verification_txt,
    ).to_dict()


@mcp.tool()
def validate_go_live(
    domain: str,
    expected_apex: str = "76.76.21.21",
    expected_www_cname: str = "cname.vercel-dns.com",
) -> dict:
    """Validate apex/www DNS mapping and produce an HTTPS go-live checklist.

    Args:
        domain: Root domain to validate, e.g. example.com
        expected_apex: Expected A record IP for the apex domain (default: Vercel's IP).
        expected_www_cname: Expected CNAME target for www (default: Vercel's CNAME).
    """
    return _validate_go_live(
        domain,
        expected_apex=expected_apex,
        expected_www_cname=expected_www_cname,
    ).to_dict()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Eno MCP Server")
    parser.add_argument("--http", action="store_true", help="Use HTTP/SSE transport (for Claude.ai web)")
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP transport (default: 8000)")
    parser.add_argument("--host", default="0.0.0.0", help="Host for HTTP transport (default: 0.0.0.0)")
    args = parser.parse_args()

    if args.http:
        # HTTP/SSE mode — for Claude.ai Integrations
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    else:
        # stdio mode — for Claude Code CLI/desktop
        mcp.run(transport="stdio")
