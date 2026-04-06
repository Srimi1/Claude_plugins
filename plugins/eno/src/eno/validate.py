from __future__ import annotations

import subprocess

from .contracts import OperationResult, STATUS_ERROR, STATUS_OK, STATUS_WARN


def _run_dig(record_type: str, host: str) -> list[str]:
    try:
        proc = subprocess.run(
            ["dig", "+short", record_type, host],
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            return []
        return [line.strip().rstrip(".") for line in proc.stdout.splitlines() if line.strip()]
    except FileNotFoundError:
        return []


def validate_go_live(
    domain: str,
    expected_apex: str = "76.76.21.21",
    expected_www_cname: str = "cname.vercel-dns.com",
) -> OperationResult:
    findings: list[str] = []
    actions: list[str] = []
    commands: list[str] = []
    next_steps: list[str] = []

    apex_records = _run_dig("A", domain)
    www_records = _run_dig("CNAME", f"www.{domain}")

    if not apex_records and not www_records:
        status = STATUS_WARN
        findings.append("DNS records could not be auto-validated (dig unavailable or no records yet).")
        actions.append("Run DNS checks manually and retry after propagation.")
    else:
        status = STATUS_OK
        if expected_apex in apex_records:
            findings.append(f"Apex A record includes expected target {expected_apex}.")
        else:
            status = STATUS_WARN
            findings.append(f"Apex A record mismatch. Found: {apex_records or ['<none>']}")
            actions.append(f"Set A record for @ to {expected_apex}.")

        normalized_www = [value.rstrip(".") for value in www_records]
        if expected_www_cname in normalized_www:
            findings.append(f"www CNAME includes expected target {expected_www_cname}.")
        else:
            status = STATUS_WARN
            findings.append(f"www CNAME mismatch. Found: {normalized_www or ['<none>']}")
            actions.append(f"Set CNAME for www to {expected_www_cname}.")

    commands.extend(
        [
            f"dig +short A {domain}",
            f"dig +short CNAME www.{domain}",
            f"curl -I https://{domain}",
            f"curl -I https://www.{domain}",
        ]
    )

    next_steps.extend(
        [
            "Confirm apex and www both resolve to your deployed project.",
            "Ensure HTTPS certificate is issued and active in Vercel.",
            "Configure 301 redirect behavior between apex and www as desired.",
        ]
    )

    if status == STATUS_OK:
        findings.append("DNS and host mapping checks look healthy for go-live.")
    elif status == STATUS_ERROR:
        next_steps.append("Fix blocking DNS issues before promoting to production.")
    else:
        next_steps.append("Re-run validate_go_live after DNS and SSL propagation.")

    return OperationResult(
        status=status,
        findings=findings,
        actions=actions,
        commands=commands,
        next_steps=next_steps,
        meta={
            "domain": domain,
            "apex_records": apex_records,
            "www_cname_records": www_records,
        },
    )
