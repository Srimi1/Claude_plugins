from __future__ import annotations

from .contracts import OperationResult, STATUS_OK


def vibe_coding_advisor() -> OperationResult:
    return OperationResult(
        status=STATUS_OK,
        findings=[
            "Phase 1 — Scope: Lock one user journey in 3 sentences before writing any prompt.",
            "Phase 2 — Build: Generate structure first (HTML/layout), then style, then behaviour.",
            "Phase 3 — Iterate: One concern per prompt; verify in browser after each change.",
            "Phase 4 — Polish: Run Lighthouse, check mobile layout, remove console errors.",
            "Phase 5 — Ship: Confirm build passes, env vars are set, git tree is clean, then deploy.",
        ],
        actions=[
            "Choose your stack before you start: static HTML for simple pages, Vite/React for interactivity, Next.js for SSR or API routes.",
            "Write a one-line goal for the page, e.g. 'A landing page that converts visitors into email subscribers.'",
            "Set a quality gate: build must pass, zero console errors, mobile layout reviewed.",
            "Use short, atomic prompts — one layout change, one style tweak, one feature at a time.",
            "After every 3–5 prompts, open the browser and review before continuing.",
            "Run 'npm run build' locally before pushing to catch pre-deploy errors early.",
            "Store all environment variables in .env.local (never commit secrets).",
            "Commit working checkpoints so you can roll back if a prompt breaks things.",
        ],
        commands=[],
        next_steps=[
            "Run analyze_project to detect project type and deployment blockers.",
            "Run prepare_deploy_vercel or prepare_deploy_netlify when ready to ship.",
            "Run guide for a complete end-to-end walkthrough.",
        ],
        meta={
            "phases": [
                {
                    "name": "1 — Scope",
                    "goal": "Define what you are building before touching code.",
                    "actions": [
                        "Write one user journey: who arrives, what they do, what they achieve.",
                        "Pick stack: static HTML/CSS/JS | Vite + React | Next.js (App Router).",
                        "List the 3 sections your page must have (e.g. hero, features, CTA).",
                    ],
                },
                {
                    "name": "2 — Build",
                    "goal": "Generate structure, then style, then behaviour.",
                    "actions": [
                        "Start with semantic HTML scaffold — no styles yet.",
                        "Add CSS/Tailwind layout (grid, flex, spacing) in a single prompt.",
                        "Add colours, typography, and brand tokens next.",
                        "Wire up interactivity last (forms, modals, fetch calls).",
                    ],
                },
                {
                    "name": "3 — Iterate",
                    "goal": "Refine one concern at a time without regressions.",
                    "actions": [
                        "One prompt per change — avoid compound requests.",
                        "Open browser preview after each change.",
                        "If something breaks, revert the last prompt and try a narrower version.",
                        "Commit a checkpoint every time the page is in a good state.",
                    ],
                },
                {
                    "name": "4 — Polish",
                    "goal": "Meet quality bar before shipping.",
                    "actions": [
                        "Run Lighthouse in Chrome DevTools and target 90+ on Performance and Accessibility.",
                        "Resize to 375px mobile width and fix any overflow or text issues.",
                        "Clear all browser console errors and warnings.",
                        "Check all links and CTA buttons work.",
                    ],
                },
                {
                    "name": "5 — Ship",
                    "goal": "Deploy with confidence.",
                    "actions": [
                        "Run npm run build locally — fix any errors before pushing.",
                        "Confirm all required environment variables are set in the deployment dashboard.",
                        "Commit all changes and push to your main branch.",
                        "Deploy via Vercel, Netlify, or GitHub Pages and run validate_go_live.",
                    ],
                },
            ],
            "stack_guide": {
                "static_html": "Best for: simple landing pages, portfolios, no build step needed. Deploy dir: project root.",
                "vite_react": "Best for: interactive SPAs, dashboards, component-heavy UIs. Deploy dir: dist/.",
                "nextjs": "Best for: SSR, API routes, image optimisation, SEO-critical pages. Deploy dir: managed by Vercel/Netlify.",
                "sveltekit": "Best for: fast, lightweight apps with minimal JS bundle. Deploy dir: build/ or via adapter.",
            },
            "prompt_templates": [
                "Create a hero section with a headline, subheading, and one CTA button using semantic HTML and responsive CSS.",
                "Add a sticky navigation bar with logo on the left and 3 nav links on the right that collapses to a hamburger on mobile.",
                "Build a 3-column features grid where each card has an icon, title, and 2-line description. Use CSS Grid.",
                "Create a contact form with name, email, and message fields. Validate required fields client-side and show inline errors.",
                "Add a smooth scroll-to-section behaviour when nav links are clicked.",
                "Refactor this component to reduce Cumulative Layout Shift and improve mobile readability.",
                "Add fetch call to POST form data to /api/subscribe and show a success or error toast message.",
                "Optimise all images with width/height attributes and lazy loading to improve Lighthouse Performance score.",
            ],
            "common_mistakes": [
                {
                    "mistake": "Changing multiple concerns in one prompt (layout + style + logic at once).",
                    "fix": "Split into three separate prompts and verify after each.",
                },
                {
                    "mistake": "Skipping a local build check before pushing to production.",
                    "fix": "Always run 'npm run build' locally first; fix errors before deploying.",
                },
                {
                    "mistake": "Committing .env files with secrets.",
                    "fix": "Add .env, .env.local to .gitignore and set secrets in the deployment dashboard.",
                },
                {
                    "mistake": "Ignoring mobile layout until the end.",
                    "fix": "Check 375px width after every build phase, not just at polish time.",
                },
                {
                    "mistake": "Not committing working checkpoints during iteration.",
                    "fix": "Git commit every time the page is in a good state so you can roll back.",
                },
                {
                    "mistake": "Asking Claude to 'make it look better' without specific criteria.",
                    "fix": "Give concrete direction: 'increase contrast on CTA button to meet WCAG AA'.",
                },
                {
                    "mistake": "Using placeholder content in production.",
                    "fix": "Replace all Lorem Ipsum and placeholder images before deploying.",
                },
                {
                    "mistake": "Skipping environment variable configuration in the deployment dashboard.",
                    "fix": "Check your .env.local file and mirror every key in Vercel/Netlify settings.",
                },
            ],
            "quality_gate_checklist": [
                "[ ] npm run build exits with code 0",
                "[ ] Zero errors and zero warnings in browser console",
                "[ ] Page renders correctly at 375px, 768px, and 1280px widths",
                "[ ] Lighthouse Performance score >= 90",
                "[ ] Lighthouse Accessibility score >= 90",
                "[ ] All CTA buttons and links are functional",
                "[ ] No placeholder text or images remain",
                "[ ] All required environment variables are set in deployment dashboard",
                "[ ] Git working tree is clean (all changes committed)",
            ],
        },
    )
