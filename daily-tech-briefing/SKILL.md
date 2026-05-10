---
name: daily-tech-briefing
description: Daily AI/Tech intelligence briefing — aggregates blogs, GitHub, YouTube, and X into a consolidated report delivered via Telegram
category: research
---

# Daily Tech Briefing
# Daily Tech Briefing

**⚠️ CRITICAL: This job has a 10-minute timeout. Follow batching strictly.**

Orchestrates parallel research across 4 data sources, aggregates findings, and delivers via Telegram.

## Timing Budget (10 min max)

| Phase | Time | Action |
|-------|------|--------|
| Spawn 3 subagents (batch 1) | 0-30s | delegate_task with 3 tasks |
| Collect batch 1 results | 30s-7min | Wait, max 6min30s |
| Spawn X/Twitter subagent (batch 2) | 7-8min | After batch 1 returns |
| Aggregate + deliver | 8-10min | Write output, direct delivery |

## Subagent Batching (CRITICAL — follow this exactly)

**Batch 1: 3 agents** (spawn together)
1. Blog/News research
2. GitHub trending
3. YouTube videos

**Batch 2: 1 agent** (spawn after batch 1 returns)
4. X/Twitter trends

**Why**: Spawning 4 subagents at once causes some to get killed. Always batch.

## Workflow

### Phase 1: Batch 1 Research (3 subagents in parallel)

**Subagent 1 — Blog/News (5-7 items max)**
```
Research latest AI/tech news from past 24-48 hours.
Sources: Hacker News (Algolia API), VentureBeat AI, TechCrunch AI.
Focus: AI tools, agents, autonomous systems, marketing automation, startup news.
Return: 5-7 items with source, title, URL, 2-3 sentence summary, why it matters.
Use API: curl "https://hn.algolia.com/api/v1/search?query=AI+agents&tags=story&hitsPerPage=7"
```

**Subagent 2 — GitHub Trending (5-7 repos max)**
```
Check GitHub trending repositories in last 30 days filtered by AI/ML.
API: curl -s "https://api.github.com/search/repositories?q=ai+machine-learning+created:>2026-03-10&sort=stars&order=desc&per_page=7"
Return: 5-7 repos with name, stars, description, business potential.
```

**Subagent 3 — YouTube Videos (5-7 videos max)**
```
Find latest videos (last 48-72h) from AI/entrepreneurship YouTube channels.
Channels: Simon Høiberg, Starter Story, Nathan Latka, Greg Isenberg, AI Engineer, Craig Hewitt, IndyDevDan.
Use web_search queries: site:youtube.com [channel] AI 2026
Return: 5-7 videos with channel, title, URL, brief summary.
```

### Phase 2: Batch 2 Research (after batch 1 returns)

**Subagent 4 — X/Twitter Trends (5-7 items max)**
```
Monitor X/Twitter for trending AI topics and posts from: balajis, naval, paulg, sama, karpathy, gdb, levelsio, rauchg.
Use web_search: "site:x.com OR site:twitter.com AI agents 2026"
Return: 5-7 notable posts with author, summary, why notable.
```

### Phase 3: Aggregation + Delivery

After all 4 subagents return:
1. Combine findings into HTML report (styled, professional)
2. Keep each item brief (2-4 sentences max)
3. Convert HTML → PDF via `wkhtmltopdf`
4. Generate voice summary via `text_to_speech` tool
5. Deliver PDF + voice via Telegram
6. Backup both files to `~/.hermes/cron/output/`

### Phase 4: File Generation

**HTML to PDF:**
```bash
wkhtmltopdf --enable-local-file-access /path/to/briefing.html /path/to/briefing.pdf
```

**Voice summary:** Use `text_to_speech` tool with output_path ending in `.ogg`. Keep under 2000 chars (60-90 sec).

**File paths (use execute_code Python, not heredoc/terminal redirect):**
```python
import os
os.makedirs('/home/openclaw/.hermes/daily-briefings', exist_ok=True)
os.makedirs('/home/openclaw/.hermes/cron/output', exist_ok=True)
with open('/home/openclaw/.hermes/daily-briefings/YYYY-MM-DD-briefing.html', 'w') as f:
    f.write(html_content)
```

### Phase 5: Telegram Delivery

**Use full target format:** `telegram:Sergio Palacio / topic 161599` — NOT `telegram:161599` and NOT `chat_id=161599`

Send in 3 separate send_message calls:
1. Summary text message (action: "send", no media)
2. PDF as media attachment — `MEDIA:/path/to/briefing.pdf`
3. Voice `.ogg` as media attachment — `MEDIA:/path/to/summary.ogg`

**If PDF media upload times out:** Send the text message + voice only; PDF is already in `~/.hermes/cron/output/` as backup.

## Hard Limits (enforce strictly)

| Limit | Reason |
|-------|--------|
| **5-7 items per stream** | 10-15 causes timeout |
| **7 minutes per subagent** | Prevents cascade timeout |
| **Batch subagents correctly** | 3 first, then 1 — never all 4 at once |
| **Skip failed streams** | Don't retry, move on |

## If Web Search Fails

If `web_search` returns no results:
1. Try direct API via `curl` (HN Algolia, GitHub API)
2. If all fail, report partial results and note which streams failed
3. Do NOT retry failed streams — move on

## Output Format

```
# Daily Tech Briefing — [DATE]

## AI/Tech News (N items)
...

## GitHub Trending (N items)
...

## YouTube Watch List (N items)
...

## X/Twitter Pulse (N items)
...
```

## Cron Configuration

```
0 5 * * * hermes chat -q "Run daily tech briefing" --skill daily-tech-briefing >> ~/.hermes/logs/daily-briefing.log 2>&1
```

**Timeout**: Must be set to 10+ minutes. If system doesn't support, split into 2 crons.

## Verification

Test with a dry run:
```bash
hermes chat -q "Run daily tech briefing for April 9 2026" --skill daily-tech-briefing
```

## Pitfalls

- ❌ Don't spawn all 4 subagents at once — some get killed
- ❌ Don't ask for 10-15 items per category — times out
- ❌ Don't use `telegram:161599` — must use `telegram:Sergio Palacio / topic 161599`
- ❌ Don't use heredoc/terminal redirect for file writing — use `execute_code` with Python `open()` instead
- ✅ Keep items brief (2-4 sentences)
- ✅ Spawn 3 first, then 4th after results return
- ✅ Use direct APIs (curl) where possible over web_search
- ✅ Use `text_to_speech` with `.ogg` output for voice summaries
- ✅ Use `wkhtmltopdf` for HTML→PDF conversion

## Content Focus
- AI tools, agents, and implementations
- Entrepreneurship case studies (especially relevant to marketing agencies)
- GitHub repos with business/application potential
- Trending topics on X
- New YouTube videos from thought leaders

## YouTube Channels to Monitor
```
Simon Høiberg
Starter Story
MicroConf
Nathan Latka
Liam Ottley
Matt Diggity
Two Minute Papers
AI Explained
Fahim LA
Mark Thompson
Y Combinator
SaaStr
Your MBA
Indie Hackers
Built In Public
Brian Casel (Caselmas)
Dan Kieft
IndyDevDan
All About AI
Builders Central
Rob Shocks
Alex Finn
Greg Isenberg
Craig Hewitt
Nick Saraev
AI Engineer
Nate Herk
Grace Leung
Ben AI
```

## X Accounts to Monitor
```
balajis, naval, paulg, sama, karpathy, gdb, garrytan, mwseibel, daltonc
levelsio, rauchg, StevenBartlett, ChrisWillx, tbpn
```

## GitHub Topics
```
ai, machine-learning, llm, ai-agents, gpt, openai, autonomous-agents
```

## Output Format

### PDF Sections
1. **Top AI/Tech News** — blog posts and articles
2. **Trending GitHub Repos** — AI/ML projects with star counts
3. **YouTube Watch List** — latest videos with summaries
4. **X/Twitter Pulse** — trending topics and key posts
5. **Entrepreneurship Opportunities** — how this connects to marketing agencies

### Voice Summary
Concise 60-90 second summary hitting the 3-4 most important developments and why they matter for a marketing agency owner.

## Technical Notes
- GitHub trending API: `https://api.github.com/search/repositories` (use `created:>YYYY-MM-DD` filter)
- HN Algolia API: `https://hn.algolia.com/api/v1/search?query=...&tags=story&hitsPerPage=7`
- X/Twitter: web_search with `site:x.com OR site:twitter.com` queries
- PDF generation: `wkhtmltopdf --enable-local-file-access` (HTML must be written via `execute_code` Python)
- TTS: `text_to_speech` tool, output `.ogg` format
- File writing: Use `execute_code` with Python `open()`, NOT terminal heredoc or `>` redirect
- Backup directory: `/home/openclaw/.hermes/cron/output/`
