from __future__ import annotations

from .contracts import OperationResult, STATUS_OK


def full_guide() -> OperationResult:
    return OperationResult(
        status=STATUS_OK,
        findings=[
            "Step 1 — Vibe Code: Use AI prompts to build your website phase by phase.",
            "Step 2 — Analyze: Run analyze_project to detect your project type and spot blockers.",
            "Step 3 — Choose platform: Vercel (best for Next.js/SSR), Netlify (great for Vite/CRA/static), GitHub Pages (free, static only).",
            "Step 4 — Prepare deploy: Run the matching prepare_deploy_* command for your platform.",
            "Step 5 — Connect domain: Run connect_domain with your registrar's provider name.",
            "Step 6 — Validate: Run validate_go_live to confirm DNS and HTTPS are live.",
        ],
        actions=[
            "Start with: eno vibe_advice — for phase-by-phase vibe coding guidance.",
            "Then run: eno analyze_project <path> — to detect project type and blockers.",
            "Choose deployment platform based on your project type (see meta.platform_guide).",
            "Run the matching deploy command, then connect_domain, then validate_go_live.",
        ],
        commands=[
            "eno vibe_advice",
            "eno analyze_project ./my-project",
            "eno prepare_deploy_vercel ./my-project",
            "eno prepare_deploy_netlify ./my-project",
            "eno prepare_deploy_github_pages ./my-project --repo-name username/repo",
            "eno connect_domain example.com --provider cloudflare",
            "eno validate_go_live example.com",
        ],
        next_steps=[
            "Run 'eno vibe_advice' to start the vibe coding workflow.",
            "After your site is built, run 'eno analyze_project <path>' to check readiness.",
        ],
        meta={
            "platform_guide": {
                "vercel": {
                    "best_for": ["nextjs", "sveltekit", "vite", "static"],
                    "free_tier": True,
                    "custom_domains": True,
                    "ssl": "automatic",
                    "command": "eno prepare_deploy_vercel ./my-project",
                    "notes": "Best choice for Next.js. Automatic preview deployments on every push.",
                },
                "netlify": {
                    "best_for": ["vite", "cra", "static", "sveltekit"],
                    "free_tier": True,
                    "custom_domains": True,
                    "ssl": "automatic",
                    "command": "eno prepare_deploy_netlify ./my-project",
                    "notes": "Great for Vite and CRA. Generous free tier with form handling and serverless functions.",
                },
                "github_pages": {
                    "best_for": ["static", "vite", "cra"],
                    "free_tier": True,
                    "custom_domains": True,
                    "ssl": "automatic",
                    "command": "eno prepare_deploy_github_pages ./my-project --repo-name username/repo",
                    "notes": "Completely free. Best for static sites. No server-side rendering support.",
                },
            },
            "dns_providers_supported": [
                "cloudflare",
                "godaddy",
                "namecheap",
                "porkbun",
                "squarespace",
                "route53",
                "generic",
            ],
            "full_workflow": [
                "1. eno vibe_advice — get phase-by-phase vibe coding guidance",
                "2. Build your site using AI prompts following the 5-phase workflow",
                "3. eno analyze_project ./my-project — detect type and blockers",
                "4. eno prepare_deploy_vercel ./my-project  (or netlify/github-pages)",
                "5. Follow commands printed by deploy step (npm build, deploy CLI)",
                "6. eno connect_domain example.com --provider <your-registrar>",
                "7. Follow DNS record instructions in your registrar dashboard",
                "8. Wait for DNS propagation (minutes to 24 hours)",
                "9. eno validate_go_live example.com — confirm apex, www, and HTTPS",
            ],
        },
    )
