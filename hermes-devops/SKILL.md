---
name: hermes-devops
description: Complete Hermes infrastructure operations — disk space recovery, emergency cleanup, Firecrawl recovery, web stack setup, system health checks, and Tailscale funnel management. Use when disk is critically full (≥95%), services are unreachable, or diagnosing infrastructure failures.
category: devops
---

# Hermes DevOps Infrastructure

Complete infrastructure operations for Hermes — disk management, service recovery, web stack setup, and system health monitoring.

**Trigger conditions**: df shows ≥95% disk usage, pip installs fail with "No space left", services unreachable on expected ports, docker permission errors, or comprehensive health verification needed.

---

## Additional Infrastructure Skills

These narrow hermes-* skills are absorbed as labeled subsections:

### hermes-cron-automation

Manages scheduled cron jobs for Hermes — create, list, pause, resume, remove.

> **Absorbed narrow skills** (use these directly for specific tasks):
> - `cron-deployment` — deploy and verify crontab entries, check script paths, replace broken `hourly_task_check.sh` references
> - `cron-management` — create, list, pause, resume, remove cron jobs
> - `cron-setup` — set up the three core cron jobs (memory consolidation, skill audit, session monitor)
> - `cron-system-recovery` — diagnose and fix crashed/missing cron entries
> - `cron-timeout-debugger` — fix cron jobs that time out consistently

See: `.archive/cron-deployment/`, `.archive/cron-management/`, `.archive/cron-setup/`, `.archive/cron-system-recovery/`, `.archive/cron-timeout-debugger/`

```bash
# Create a cron job
hermes cron create --name "daily health check" \
  --skill hermes-devops \
  --prompt "Run system health check and report issues" \
  --schedule "0 6 * * *"

# List all cron jobs
hermes cron list

# Pause a job
hermes cron pause <job_id>

# Remove a job
hermes cron remove <job_id>
```

Key concepts: jobs run in fresh sessions with no current-chat context; use `--deliver origin` for results to return to the originating conversation; skills are loaded automatically when specified; `context_from` chains outputs between jobs.

### hermes-peak-config

Audits and maintains Hermes agent at peak configuration — verifies installed skills, credentials, tool availability, and agent readiness.

**Trigger**: When the user says "check my hermes setup" or "is hermes configured correctly?"

```bash
# Run peak config audit
hermes chat -q "Run peak config audit"

# Check specific component
hermes tools list
hermes skills list
hermes config show
```

### hermes-profiles

Creates, configures, and manages multiple Hermes profiles for different roles or contexts.

```bash
# List profiles
hermes profiles list

# Create a new profile
hermes profiles create --name work --model claude-sonnet-4

# Switch profile
hermes profiles activate work

# Show current profile
hermes profiles current
```

### hermes-browser-automation

Complete browser automation workflow using Hermes MCP browser tools — navigation, clicking, typing, snapshots, vision analysis.

```bash
# Navigate to URL
hermes browser navigate https://example.com

# Take snapshot
hermes browser snapshot

# Click element
hermes browser click @e5

# Type into field
hermes browser type @e3 "search query"

# Scroll
hermes browser scroll down

# Vision analysis
hermes browser vision "What is on the page?"
```

Key MCP tools: `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, `browser_scroll`, `browser_vision`. Requires Camofox running at port 9377.

### hermes-telegram-automation

Complete Telegram bot lifecycle for Hermes — setup, configure, and manage Telegram bots as delivery channels.

**Trigger**: User wants to set up a new Telegram bot, troubleshoot delivery failures, or configure Telegram as a Hermes delivery target.

```bash
# Setup new bot
hermes telegram setup --bot-token <token> --channel @mychannel

# Check bot status
hermes telegram status

# Test delivery
hermes telegram send --test "Hello from Hermes"
```

Key concepts: Telegram bots use bot tokens; delivery requires the bot to have been started by the user first (Telegram API restriction); configure via `hermes config set telegram.bot_token <token>`.

---

## Skill Map

| Task | Use This Skill |
|------|---------------|
| Emergency disk recovery (≥95% full) | → `disk-emergency-recovery` subsection below |
| Routine disk cleanup (filling up) | → `disk-space-maintenance` subsection below |
| Firecrawl Docker permission/connectivity issues | → `firecrawl-recovery` subsection below |
| Web stack setup (Firecrawl + SearXNG + Camofox) | → `web-stack-setup` subsection below |
| Comprehensive health check of all services | → `system-health-check` subsection below |
| Tailscale funnel configuration | → `tailscale-funnel-management` subsection below |
| MemOS setup and verification | → `memos-setup` subsection below |

---

## Architecture Overview

| Service | Port | Purpose | Docker? |
|---------|------|---------|---------|
| Firecrawl | 3002 | Web search + scrape + Playwright | Yes |
| SearXNG | 8888 | Meta-search (inside Firecrawl compose) | Yes |
| Camofox | 9377 | Anti-bot Firefox with fingerprint spoofing | No |
| MemOS | 8001 | Memory system for agents | No |
| Hermes Gateway | 3001 | Message routing | No |

---

## disk-emergency-recovery

Emergency disk space recovery when system is critically full. Target known large temporary directories that can be safely removed.

**Trigger**: `df -h /` shows ≥95% used, OR pip installs fail with "No space left", OR du commands timeout.

### Step-by-Step Recovery

**Step 1: Diagnose Fast**
```bash
df -h /
du -sh /tmp/* 2>/dev/null | sort -rh | head -10
ps aux --sort=-%mem | head 10
```

**Step 2: Target Known Large Temp Dirs (in order)**
```bash
# MiroFish venv in /tmp (safe to remove — Docker handles apps)
du -sh /tmp/MiroFish/backend/.venv 2>/dev/null && rm -rf /tmp/MiroFish/backend/.venv

# pip uninstall temp files
du -sh /tmp/pip-unpack-* 2>/dev/null && rm -rf /tmp/pip-unpack-*

# cargo build temp
du -sh /tmp/cargo-install* 2>/dev/null && rm -rf /tmp/cargo-install*

# npm/node cache in /tmp
du -sh /tmp/npm-* 2>/dev/null && rm -rf /tmp/npm-*
```

**Step 3: Check HuggingFace Cache**
```bash
du -sh ~/.cache/huggingface/hub/*/  2>/dev/null | sort -rh | head -10

# Remove dormant models (not sentence-transformers/all-MiniLM-L6-v2 which MemOS needs)
# Safe to remove: Twitter/twhin-bert-base (1.1GB, likely dormant)
rm -rf ~/.cache/huggingface/hub/models--Twitter--twhin-bert-base
```

**Step 4: Clean Package Manager Caches**
```bash
pip cache purge 2>/dev/null || true
sudo apt clean 2>/dev/null || true
docker system prune -af --volumes 2>/dev/null || true
```

**Step 5: Verify Recovery**
```bash
df -h /
du -sh /tmp/* 2>/dev/null | sort -rh | head -5
```

### Typical Recovery Results

| Target | Space Freed |
|--------|-------------|
| MiroFish .venv | 7-10 GB |
| pip temp | 1-3 GB |
| cargo temp | 1-2 GB |
| HF cache (dormant) | 0.5-2 GB |
| **Total** | **10-17 GB** |

### Keep vs Remove

**KEEP (DO NOT DELETE)**
- `~/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2` — MemOS embedder
- `~/.cache/huggingface/hub/models--systran--faster-whisper-base` — Whisper potentially in use
- Any model currently loaded or recently used

**REMOVE (Safe)**
- `Twitter/twhin-bert-base` — 1.1GB, dormant
- `/tmp/MiroFish/backend/.venv` — Docker handles the app, venv not needed
- `/tmp/pip-unpack-*` — pip install leftovers
- `/tmp/cargo-install*` — cargo build leftovers

### Pitfalls
- ❌ Do NOT delete `/tmp` itself — only its contents
- ❌ Do NOT delete `~/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2` — MemOS embedder breaks
- ❌ Do NOT delete `~/.cache/huggingface/hub/models--systran--faster-whisper-base` without checking
- ✅ Always `du -sh <path>` before deleting to confirm size
- ✅ After cleanup, restart any services that may have cached data in memory

---

## disk-space-maintenance

Diagnose disk usage and clean up unnecessary files to free space.

### Step 1 — Check Disk Usage
```bash
df -h /
du -sh /home/* 2>/dev/null | sort -h
du -sh /tmp/* 2>/dev/null | sort -h
```

### Step 2 — Identify Common Culprits

| Path | Size | What to Do |
|------|------|------------|
| `/home/openclaw/.cache/` | Large | `rm -rf /home/openclaw/.cache/*` |
| `/tmp/cargo-install*` | Large | `rm -rf /tmp/cargo-install*` |
| `/tmp/pip-unpack-*` | Large | `rm -rf /tmp/pip-unpack-*` |
| `/tmp/MiroFish/` | Large | `rm -rf /tmp/MiroFish/` |
| Docker images | Large | `docker system prune -a` |
| Whisper cache | 3.6GB | `rm -rf ~/.cache/whisper` |

### Step 3 — Clean Up Commands

**Safe cleanup (auto-approved):**
```bash
rm -rf /tmp/pip-unpack-* 2>/dev/null
rm -rf /tmp/cargo-install* 2>/dev/null
rm -rf /home/openclaw/.cache/pip 2>/dev/null
```

**Requires approval (recursive delete):**
```bash
rm -rf /tmp/MiroFish
rm -rf /home/openclaw/.cache/whisper
docker system prune -a
```

### Step 4 — Verify
```bash
df -h /
```
Target: at least 10GB free.

### Common Patterns Found

**Apr 16 2026 Session:**
1. MiroFish venv in /tmp — `rm -rf /tmp/MiroFish/backend/.venv`
2. Pip uninstall artifacts — `rm -rf /tmp/pip-unpack-*`
3. Cargo build temp — `rm -rf /tmp/cargo-install*`
4. Whisper cache (3.6G!) — `rm -rf /home/openclaw/.cache/whisper`

### Pitfalls
- ❌ Don't delete Docker images if other services depend on them
- ❌ Don't delete Whisper cache if you use speech transcription regularly
- ✅ Always check `df -h` before and after to confirm space freed
- ✅ If disk is 99% full, installations will fail mid-way — clean first, then install

---

## firecrawl-recovery

Fix Firecrawl (port 3002) when it's unreachable, crashing, or failing to start due to Docker permission errors.

### Diagnosis First
```bash
curl -s --connect-timeout 3 http://localhost:3002/health
docker ps 2>&1
docker compose -f ~/.openclaw/workspace/firecrawl/docker-compose.yml ps 2>&1
```

### Error 1: "permission denied while trying to connect to the Docker daemon"

**Root cause**: Shell session started before user was added to docker group, or SSH session didn't reload groups.

**Fix — Option 1 (current session fix):**
```bash
newgrp docker
cd ~/.openclaw/workspace/firecrawl && docker compose up -d
```

**Fix — Option 2 (persistent — requires logout):**
```bash
# User was added to docker group but session not reloaded
logout && ssh openclaw@host
```

**Fix — Option 3 (for cron jobs):**
```cron
@reboot sleep 30 && sg docker -c "cd ~/.openclaw/workspace/firecrawl && docker compose up -d"
```

**Fix — Option 4 (systemd user service — recommended):**
```bash
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/firecrawl.service << 'EOF'
[Unit]
Description=Firecrawl Docker Compose
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=%h/.openclaw/workspace/firecrawl
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now firecrawl
```

### Error 2: "Cannot connect to the Docker daemon at unix:///var/run/docker.sock"

**Fix:**
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### Error 3: Container exits immediately or restarts in a loop
```bash
docker logs firecrawl-app-1 2>&1 | tail -50

# Check env file
cat ~/.openclaw/workspace/firecrawl/.env

# Check port conflicts
ss -tlnp | grep 3002

# Rebuild from scratch
cd ~/.openclaw/workspace/firecrawl
docker compose down -v
docker compose up -d --build
```

### Error 4: Firecrawl healthy but web_search returns NoneType errors

**Symptom**: `curl localhost:3002/health` returns `{"status":"healthy"}` but `mcp_web_search` fails.

**Fix:**
```bash
# Check SearXNG
curl -s "localhost:8888/search?q=test&format=json" | head -c 100

# Restart both
cd ~/.openclaw/workspace/firecrawl && docker compose restart
```

### Full Recovery Sequence
```bash
# Step 1: Activate docker group
newgrp docker

# Step 2: Check Docker
docker ps 2>&1

# Step 3: Start Firecrawl
cd ~/.openclaw/workspace/firecrawl && docker compose up -d

# Step 4: Wait and verify
sleep 5
curl -s localhost:3002/health
curl -s "localhost:8888/search?q=test&format=json" | head -c 100

# Step 5: Test web search
```

### Fallback: Direct API Without Firecrawl

| Source | API/Method |
|--------|------------|
| Hacker News | `curl "https://hn.algolia.com/api/v1/search?query=AI&tags=story&hitsPerPage=5"` |
| GitHub | `curl "https://api.github.com/search/repositories?q=ai+created:>2026-04-01&sort=stars&order=desc&per_page=5"` |
| SearXNG | `curl "http://localhost:8888/search?q=...&format=json"` |

### Files & Paths

| Path | Purpose |
|------|---------|
| `~/.openclaw/workspace/firecrawl/` | Firecrawl source + docker-compose |
| `~/.openclaw/workspace/firecrawl/.env` | API keys (FIRECRAWL_API_KEY, etc.) |
| `/var/run/docker.sock` | Docker daemon socket |
| `~/.config/systemd/user/firecrawl.service` | Systemd user service (optional) |

### Pitfalls
- ❌ Don't run `docker compose up -d` without first activating docker group if `newgrp` was needed
- ❌ Docker daemon starts on boot via systemd — if it failed, cron Firecrawl starts will silently fail
- ❌ `newgrp docker` only affects current shell — cron jobs need `sg docker` or systemd service
- ✅ Always check `docker logs <container>` before rebuilding

---

## web-stack-setup

Bootstrap and repair the Hermes web research stack — Firecrawl, SearXNG, and Camofox.

### Architecture

| Service | Port | Purpose | Docker? |
|---------|------|---------|---------|
| Firecrawl | 3002 | Web search + scrape + Playwright | Yes |
| SearXNG | 8888 | Meta-search (inside Firecrawl compose) | Yes |
| Camofox | 9377 | Anti-bot Firefox | No |

### Setup Script
```bash
#!/bin/bash
set -e

echo "=== Hermes Web Stack Setup ==="

# Firecrawl (includes SearXNG)
cd ~/.openclaw/workspace/firecrawl
docker compose up -d
sleep 3
curl -s localhost:3002/health && echo " ✅ Firecrawl UP" || echo " ❌ Firecrawl DOWN"
curl -s "localhost:8888/search?q=test&format=json" | head -c 100 && echo " ✅ SearXNG UP" || echo " ❌ SearXNG DOWN"

# Camofox
if ! curl -s localhost:9377/health | grep -q "ok"; then
  camofox --port 9377 &
  sleep 2
  curl -s localhost:9377/health && echo " ✅ Camofox UP" || echo " ❌ Camofox DOWN"
else
  echo " ✅ Camofox already running"
fi
```

### Step-by-Step Setup

**Step 1: Firecrawl + SearXNG (Docker)**
```bash
docker ps -a --filter "name=firecrawl"
cd ~/.openclaw/workspace/firecrawl
docker compose up -d
curl -s localhost:3002/health
curl -s "localhost:8888/search?q=test&format=json" | head -c 200
```

**Step 2: Camofox (if not running)**
```bash
curl -s localhost:9377/health
# If down:
camofox --port 9377 &
sleep 3
curl -s localhost:9377/health
```

**Step 3: Verify all services**
```bash
curl -s localhost:3002/v1/search -X POST -H "Content-Type: application/json" \
  -d '{"query":"test","limit":1}'
```

### Common Fixes

**Firecrawl DOWN:**
```bash
cd ~/.openclaw/workspace/firecrawl
docker compose down
docker compose up -d
docker logs firecrawl-app -f
```

**SearXNG DOWN (but Firecrawl up):**
```bash
cd ~/.openclaw/workspace/firecrawl
docker compose restart searxng
```

**Camofox DOWN:**
```bash
pkill -f camofox || true
camofox --port 9377 &
sleep 3
curl -s localhost:9377/health
```

**Web search returns no results:**
- Check Firecrawl is healthy: `curl localhost:3002/health`
- Check `FIRECRAWL_API_KEY` in `.env` if using cloud
- Check `BRAVE_API_KEY` if using Brave backend

### Cron Auto-Start
```
@reboot cd ~/.openclaw/workspace/firecrawl && docker compose up -d
@reboot camofox --port 9377 &
```

### Pitfalls
- Firecrawl docker-compose must be in `~/.openclaw/workspace/firecrawl/`
- Camofox port MUST be 9377 (hardcoded in Hermes browser tools)
- SearXNG is inside Firecrawl's compose file, not standalone

---

## system-health-check

Run a comprehensive health check across all Hermes infrastructure services.

### Services to Check

| Service | Endpoint | Expected Response |
|---------|----------|-------------------|
| Camofox | `localhost:9377/health` | `ok` |
| Firecrawl | `localhost:3002/health` | healthy JSON |
| SearXNG | `localhost:8888/search?q=test&format=json` | JSON results |
| MemOS | `localhost:8001/health` | healthy JSON |
| Hermes Doctor | `hermes doctor 2>&1` | no errors |
| Docker | `docker ps -a --filter "name=firecrawl"` | running |

### Run All Checks in Parallel
```bash
echo "=== System Health Check $(date) ===" && \
echo "--- Camofox ---" && curl -s localhost:9377/health && \
echo "--- Firecrawl ---" && curl -s localhost:3002/health 2>&1 || echo "Firecrawl DOWN" && \
echo "--- SearXNG ---" && curl -s "localhost:8888/search?q=test&format=json" | head -c 200 && \
echo "--- MemOS ---" && curl -s localhost:8001/health && \
echo "--- Hermes Doctor ---" && hermes doctor 2>&1 && \
echo "--- Docker ---" && docker ps -a --filter "name=firecrawl" --format "{{.Names}} {{.Status}}" && \
echo "--- Cron Jobs ---" && crontab -l 2>&1 | head -10
```

### If Something is Down

**Firecrawl DOWN:**
```bash
cd ~/.openclaw/workspace/firecrawl && docker compose up -d
```

**Camofox DOWN:**
```bash
ps aux | grep camofox | grep -v grep
camofox --port 9377 &
```

**MemOS DOWN:**
```bash
cd /home/openclaw/Coding/MemOS && python -m memos.api.server &
```

### Cron Job Pattern
This is typically run as a cron job before other critical tasks:
```
0 5 * * * hermes chat -q "Run system health check" --skill system-health-check >> ~/.hermes/logs/health-check.log 2>&1
```

### Pitfalls
- Don't run checks sequentially if you can run them in parallel via semicolons
- Firecrawl health endpoint may be `/` not `/health` — test both
- If `hermes doctor` fails, the hermes binary may not be in PATH

---

## tailscale-funnel-management

Diagnose and fix Tailscale Funnel misconfiguration issues.

### Prerequisites
- Tailscale must be installed and authenticated
- Funnel must be enabled on the tailnet: `tailscale funnel on`
- Cloud firewall must allow the funnel port (usually 80)

### Diagnosis Steps

**Step 1: Check Current Funnel Status**
```bash
tailscale funnel status
```

**Step 2: Test Backend Services**
```bash
curl -sv http://localhost:PORT
```

**Step 3: Verify Funnel Configuration**
```bash
tailscale funnel --bg=false status
```

### Common Fix Patterns

**Reset and Reconfigure Funnel:**
```bash
tailscale funnel --bg=false reset
tailscale funnel on --bg=false 0.0.0.0:80
tailscale funnel 3000
```

**Update an Existing Mapping:**
```bash
tailscale funnel --bg=false 3000
```

### Pitfalls
- Backend must listen on localhost — Funnel proxies from 127.0.0.1
- After reset, re-add all mappings
- Funnel provides HTTP only, not HTTPS

---

## memos-setup

Provision and verify the MemOS memory system for Hermes agents.

### Prerequisites
- Python 3.14 at `/home/linuxbrew/.linuxbrew/opt/python@3.14/bin/python3.14`
- `memos` package: `pip install memos`
- MemOS source at `/home/openclaw/Coding/MemOS/`

### Step-by-Step Setup

**Step 1: Verify Python 3.14 and memos package**
```bash
python3 --version  # Must be 3.14.x
python3 -c "import memos; print('memos OK:', memos.__file__)"
```

**Step 2: Check MemOS server health**
```bash
curl -s http://127.0.0.1:8001/health
# Expected: {"status":"healthy","service":"memos","version":"1.0.1"}
```

**Step 3: If server is down, start it**
```bash
cd /home/openclaw/Coding/MemOS
bash start-memos.sh >> ~/.hermes/logs/memos.log 2>&1 &
# OR if start-memos.sh doesn't exist:
python3 -m memos.api.server &
```

**Step 4: Verify MemOS is responding**
```bash
curl -s http://127.0.0.1:8001/openapi.json | head -50
```

**Step 5: Provision agents (if setting up fresh)**
```bash
cd /home/openclaw/Coding/MemOS
python3 setup-memos-agents.py
```

**Step 6: Verify agent cubes exist**
```bash
curl -s http://127.0.0.1:8001/api/v1/cubes | python3 -m json.tool
```

### Crontab Setup for @reboot
```cron
@reboot source ~/.hermes/venv/bin/activate && cd /home/openclaw/Coding/MemOS && bash start-memos.sh >> ~/.hermes/logs/memos.log 2>&1 &
```

### Common Issues

**"ModuleNotFoundError: No module named 'pydantic_core'"**
System Python (3.12) is trying to load memos installed for Python 3.14. Always use `python3` which resolves to 3.14.

**MemOS health returns 404:**
Try `/openapi.json` or `/api/v1/health`.

**"port already in use":**
```bash
pkill -f "memos.api.server" || pkill -f "python.*memos"
```

### Verification Checklist
- [ ] `curl http://127.0.0.1:8001/health` returns healthy
- [ ] `curl http://127.0.0.1:8001/openapi.json` returns OpenAPI spec
- [ ] Agent cubes are provisioned
- [ ] @reboot entry exists in crontab
- [ ] `python3 -c "import memos"` works
