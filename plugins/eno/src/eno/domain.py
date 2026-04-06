from __future__ import annotations

from .contracts import OperationResult, STATUS_OK, STATUS_WARN

SUPPORTED_PROVIDERS = {"generic", "cloudflare", "godaddy", "namecheap", "porkbun", "squarespace", "route53"}


def _generic_records(domain: str, apex_target: str, www_target: str) -> list[dict[str, str]]:
    return [
        {
            "type": "A",
            "name": "@",
            "value": apex_target,
            "notes": "Apex/root domain target for your deployment provider.",
        },
        {
            "type": "CNAME",
            "name": "www",
            "value": www_target,
            "notes": "Redirect www to deployment hostname.",
        },
    ]


def _provider_template(provider: str) -> list[str]:
    if provider == "cloudflare":
        return [
            "DNS -> Add A record for @ and CNAME for www.",
            "Set Proxy status to DNS only until SSL is confirmed.",
            "After certificate is active, optionally enable proxy.",
        ]
    if provider == "godaddy":
        return [
            "My Products -> DNS -> Manage Zone.",
            "Add A record (@) and CNAME record (www).",
            "Remove conflicting old A/CNAME records before saving.",
        ]
    if provider == "namecheap":
        return [
            "Domain List -> Manage -> Advanced DNS.",
            "Create Host Records for @ (A) and www (CNAME).",
            "Disable old URL redirect records that override DNS.",
        ]
    if provider == "porkbun":
        return [
            "Log in to Porkbun -> Domain Management -> DNS.",
            "Add A record: host = (blank or @), answer = apex IP.",
            "Add CNAME record: host = www, answer = deployment CNAME hostname.",
            "Delete any existing conflicting A or CNAME records first.",
        ]
    if provider == "squarespace":
        return [
            "Log in to Squarespace (formerly Google Domains) -> Select domain -> DNS.",
            "Go to Custom Records and click Add record.",
            "Add A record: host = @, data = apex IP.",
            "Add CNAME record: host = www, data = deployment CNAME hostname.",
        ]
    if provider == "route53":
        return [
            "Open AWS Console -> Route 53 -> Hosted zones -> select your domain.",
            "Click Create record, set Type = A, Name = (empty for apex), Value = apex IP.",
            "Click Create record again, set Type = CNAME, Name = www, Value = deployment CNAME hostname.",
            "Set TTL to 300 for faster propagation during initial setup.",
        ]
    return [
        "Add A record for @ and CNAME for www in your DNS panel.",
        "If provider asks for verification, add TXT records exactly as provided by your deployment platform.",
    ]


def connect_domain(
    domain: str,
    provider: str = "generic",
    apex_target: str = "76.76.21.21",
    www_target: str = "cname.vercel-dns.com",
    needs_verification_txt: bool = False,
) -> OperationResult:
    provider_normalized = provider.strip().lower()
    status = STATUS_OK
    findings: list[str] = []

    if provider_normalized not in SUPPORTED_PROVIDERS:
        status = STATUS_WARN
        findings.append(
            f"Provider '{provider}' is not in supported templates; using generic DNS guidance."
        )
        provider_normalized = "generic"
    else:
        findings.append(f"Using {provider_normalized} DNS template for domain {domain}.")

    records = _generic_records(domain, apex_target, www_target)
    if needs_verification_txt:
        records.append(
            {
                "type": "TXT",
                "name": "_vercel",
                "value": "<verification-token-from-vercel>",
                "notes": "Only required if Vercel asks for domain ownership verification.",
            }
        )

    actions = _provider_template(provider_normalized)
    next_steps = [
        "Add records in your registrar DNS panel.",
        "Wait for propagation (typically minutes, can take up to 24 hours).",
        "In Vercel domain settings, verify domain and enforce HTTPS.",
        "Run validate_go_live to verify apex, www, and SSL behavior.",
    ]

    commands = [
        f"dig +short A {domain}",
        f"dig +short CNAME www.{domain}",
        f"nslookup {domain}",
    ]

    return OperationResult(
        status=status,
        findings=findings,
        actions=actions,
        commands=commands,
        next_steps=next_steps,
        meta={
            "provider": provider_normalized,
            "domain": domain,
            "records": records,
        },
    )
