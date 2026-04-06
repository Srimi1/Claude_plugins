"""Eno MCP Server — exposes Eno capabilities as Claude tools via MCP stdio transport."""
from __future__ import annotations

import sys
import os

# Allow running directly without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mcp.server.fastmcp import FastMCP

from eno.analyze import analyze_project as _analyze_project
from eno.deploy import prepare_deploy_vercel as _prepare_deploy_vercel
from eno.domain import connect_domain as _connect_domain
from eno.validate import validate_go_live as _validate_go_live
from eno.vibe_advisor import vibe_coding_advisor as _vibe_coding_advisor

mcp = FastMCP("Eno")


@mcp.tool()
def vibe_coding_advisor() -> dict:
    """Get practical vibe-coding guidance: prompts, readiness checklists, and common mistakes with fixes."""
    return _vibe_coding_advisor().to_dict()


@mcp.tool()
def analyze_project(project_path: str) -> dict:
    """Detect whether a project is static or Next.js, and report any deployment blockers.

    Args:
        project_path: Absolute or relative path to the project directory.
    """
    return _analyze_project(project_path).to_dict()


@mcp.tool()
def prepare_deploy_vercel(project_path: str, run_automation: bool = False) -> dict:
    """Generate a Vercel deployment checklist, commands, and GitHub readiness checks.

    Args:
        project_path: Absolute or relative path to the project directory.
        run_automation: When True, marks the deploy sequence for automated execution.
    """
    return _prepare_deploy_vercel(project_path, run_automation=run_automation).to_dict()


@mcp.tool()
def connect_domain(
    domain: str,
    provider: str = "generic",
    needs_verification_txt: bool = False,
) -> dict:
    """Generate DNS records and provider-specific instructions to connect a custom domain on Vercel.

    Args:
        domain: Root domain to connect, e.g. example.com
        provider: DNS provider — one of: generic, cloudflare, godaddy, namecheap
        needs_verification_txt: Set True if Vercel requires a TXT ownership verification record.
    """
    return _connect_domain(domain, provider=provider, needs_verification_txt=needs_verification_txt).to_dict()


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
    mcp.run()
