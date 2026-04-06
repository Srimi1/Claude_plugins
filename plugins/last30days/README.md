# last30days Skill

**Version:** 2.9.6  
**Source:** https://github.com/mvanhorn/last30days-skill  
**Installed at:** `~/.claude/skills/last30days`

A deep research engine that searches 10+ platforms for content from the last 30 days and synthesizes findings into expert-level briefings with citations.

## Sources

| Source | Requires |
|--------|----------|
| Reddit | No key (public API) |
| Hacker News | No key (public API) |
| Polymarket | No key (public API) |
| X/Twitter | `XAI_API_KEY` or Bird CLI |
| YouTube | `yt-dlp` installed |
| TikTok/Instagram | `SCRAPECREATORS_API_KEY` |
| Web search | `BRAVE_API_KEY`, `PARALLEL_API_KEY`, or `OPENROUTER_API_KEY` |
| Bluesky | Bluesky app password |

## Usage

```
/last30days [topic]
/last30days [topic] vs [topic2]       # Comparative mode
/last30days [topic] --quick           # Faster, fewer sources
/last30days [topic] --deep            # More thorough
/last30days [topic] --days=7          # Custom time window
/last30days --diagnose                # Check source availability
```

## Configuration

API keys go in `~/.config/last30days/.env` or `.claude/last30days.env` (project-local).

## Installation

```bash
git clone https://github.com/mvanhorn/last30days-skill.git ~/.claude/skills/last30days
```
