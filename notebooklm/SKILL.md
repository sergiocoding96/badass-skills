---
name: notebooklm
description: Complete API for Google NotebookLM - full programmatic access including features not in the web UI. Create notebooks, add sources, generate all artifact types, download in multiple formats. Activates on explicit /notebooklm or intent like "create a podcast about X", "install notebooklm", "add notebooklm to cowork"
---
<!-- notebooklm-py v0.3.4 -->

# NotebookLM Automation

Complete programmatic access to Google NotebookLM—including capabilities not exposed in the web UI. Create notebooks, add sources (URLs, YouTube, PDFs, audio, video, images), chat with content, generate all artifact types, and download results in multiple formats.

## Step 0: Setup (Run Automatically on First Use)

When this skill is triggered and `notebooklm` is not yet installed or authenticated, complete setup first.

### Pre-flight: Check Python Version

`notebooklm-py` requires **Python 3.10+**. Check the available version before installing:

```bash
python3 --version
```

If Python is below 3.10 (e.g. 3.9.x which is the macOS default), install a compatible version:

**macOS (Homebrew):**
```bash
brew install python@3.12
```
Then use `/opt/homebrew/bin/python3.12` (Apple Silicon) or `/usr/local/bin/python3.12` (Intel) for the venv below.

**Linux (apt):**
```bash
sudo apt update && sudo apt install -y python3.12 python3.12-venv
```

### Install the CLI

Always use a virtual environment to avoid "externally-managed-environment" errors and PATH issues.

Determine which Python to use — if the system `python3` is 3.10+, use it directly. Otherwise use the one you just installed (e.g. `python3.12`):

```bash
# Set PYTHON to the correct binary (adjust if needed)
PYTHON=$(command -v python3.12 2>/dev/null || command -v python3.11 2>/dev/null || command -v python3.10 2>/dev/null || command -v python3)

# Verify it's 3.10+
$PYTHON -c "import sys; assert sys.version_info >= (3,10), f'Python {sys.version} is too old — need 3.10+'; print(f'Using Python {sys.version}')"

# Create venv and install
$PYTHON -m venv ~/.notebooklm-venv
source ~/.notebooklm-venv/bin/activate
pip install "notebooklm-py[browser]"
playwright install chromium
```

Then symlink so it's always on PATH:
```bash
mkdir -p ~/bin
ln -sf ~/.notebooklm-venv/bin/notebooklm ~/bin/notebooklm
export PATH="$HOME/bin:$PATH"
```

Verify the CLI works:
```bash
notebooklm --help
```

### Authenticate

**IMPORTANT:** The built-in `notebooklm login` command and the Playwright-based login script both open a browser on the **remote server**, not on the user's local machine. This means in a headless/server environment, the browser will never be visible to the user and auth will fail silently or hang.

**IMPORTANT — Auth model mismatch:** `notebooklm-py` uses **Google session cookies** (SID, HSID, APISID, SAPISID) stored in a Playwright `storage_state.json`. It does **NOT** accept OAuth2 access tokens or ID tokens — those are for Google REST APIs (Drive, Gmail, Calendar) and cannot authenticate the NotebookLM CLI. If you already have a `google_token.json` with OAuth tokens, they are useless for this skill — you still need browser-based Google sign-in.

**Three working paths — pick one:**

**Path A (recommended): Local machine auth + copy**  
Run `notebooklm login` on the user's **local machine** (where the browser IS visible), then copy `~/.notebooklm/profiles/default/storage_state.json` to the server at the same path.

**Path B: Hermes browser interactive auth (headless server)**  \nOn a headless server, use the Hermes browser tool to navigate to notebooklm.google.com and complete Google sign-in interactively:

Step 1 — Navigate and fill email
```
browser_navigate("https://notebooklm.google.com/")
browser_type("@e1", "user@gmail.com")
browser_click("@e4")  # Next
```

Step 2 — Enter password
After clicking Next, wait for the "Hi [Name]" / "Enter your password" screen (check with browser_snapshot). Ask the user for the password — never guess it.
```
browser_type("@e2", "<password-from-user>")
browser_click("@e4")  # Next
```

Step 3 — Navigate account recovery prompts
On first sign-in from a new device, Google may show setup screens. These are not errors — skip through them:
- Recovery phone: Click "Cancel" (@e4)
- Home address: Click "Skip" (@e2)
- Any other prompt: Look for "Skip" or "Cancel" buttons

Step 4 — Verify
After prompts clear, the browser reaches https://notebooklm.google.com/ — confirm via browser_snapshot (you should see "Create new notebook" and/or the NotebookLM logo).

Step 5 — Save storage state for CLI
The Hermes browser may use **Chromium** or **Firefox** as its Playwright engine. The cookie storage method differs by engine.

**First, detect which engine is in use:**
```bash
ls /tmp/ | grep playwright_
# playwright_chromiumdev_profile-*  → Chromium (cookies in memory)
# playwright_firefoxdev_profile-*    → Firefox (cookies on disk)
```

**If Firefox (cookies on disk):**
See `references/firefox-cookie-extraction.md` for the complete recipe. Cookies live in `/tmp/playwright_firefoxdev_profile-*/cookies.sqlite`, can be copied (DB is locked while Playwright runs), and converted to Playwright storage_state.json format.

**If Chromium (cookies in memory):**
The temp profile has a `Default/Cookies` SQLite file but it's typically empty (just schema, 0 rows). Cookies are truly in-memory. To save them:

Option A — Reuse temp profile (best when profile still exists):
Find the temp profile path from `ps aux | grep playwright` (--user-data-dir=/tmp/playwright_chromiumdev_profile-*), then use a Playwright Python script with that profile to call `browser.storage_state()`.

Option B — Direct browser interaction (no CLI needed):
Once authenticated in the Hermes browser, just use browser_navigate, browser_click, and browser_type to interact with NotebookLM directly. All major features (list notebooks, open notebooks, add sources, view content) are accessible via the web UI. CLI-only features (batch downloads, programmatic generation) won't be available.

**Path C: Google Cloud OAuth2**  
Set up a Google Cloud project with NotebookLM API enabled, use `oauthlib` to get refresh tokens, and configure `notebooklm` with service account credentials. Requires Google Cloud setup. Not tested.

The Playwright browser-based login script (below) only works when running **on the same machine where the user can see the browser** — it is NOT a remote browser redirect. Do not attempt to use it in a headless/server environment unless you have Xvfb and can stream the display.

### Pitfall: `--browser-cookies` on Linux

The `notebooklm login --browser-cookies chrome` command fails on modern Linux with Chrome because cookies are encrypted with AES-256-CBC using a key stored in the system keyring (libsecret/gnome-keyring). `rookiepy` cannot decrypt them without access to that key. The database shows cookie values as encrypted blobs — SQLite queries confirm the `value` field is empty and `encrypted_value` contains 67-195 bytes per cookie. If this fails, fall back to Path A or B. Installing `browser-cookie3` gives a similar error (`Unable to get key for cookie decryption`). Do NOT retry the same command — switch auth paths.

### Pitfall: OAuth token ≠ NotebookLM session

If the user says "use the OAuth token" — clarify that NotebookLM uses browser cookies, not OAuth. The token works for Drive/Gmail/Calendar REST APIs but can't authenticate the `notebooklm-py` CLI. Direct API calls with `Authorization: Bearer <token>` to `notebooklm.google.com` endpoints return 405 or redirect to Google sign-in.

### Pitfall: `notebooklm auth check` can falsely report ✓ pass with stale cookies

`notebooklm auth check` only validates that the `storage_state.json` file exists, is valid JSON, and contains an SID cookie with the right name. It does NOT verify the cookie is still valid with Google's servers. You can get ✓ pass on all checks and still fail on the next API call.

**Always verify auth with a real API call** before proceeding:
```bash
notebooklm list
```
If this returns an `Authentication expired` error with a redirect URL, the cookies are stale even if `auth check` passed. Re-run `notebooklm login`.

The error message to look for:
```
Authentication expired or invalid. Redirected to: https://accounts.google.com/v3/signin/...
```

### Pitfall: Hermes browser may use Firefox (not Chromium) — cookies persist to disk

The existing pitfall below assumes Hermes browser always uses Playwright Chromium. On some systems, Hermes uses **Firefox** instead. Check with:
```bash
ls /tmp/ | grep playwright_firefox
```

When Firefox is used, cookies ARE stored on disk — see `references/firefox-cookie-extraction.md` for the full extraction workflow.
When Chromium is used (the default assumption below), cookies are in-memory only.

### Pitfall: Hermes browser in-memory cookies (Chromium only)

When using the Hermes browser tool for auth with Playwright Chromium, cookies are stored in memory, not on disk. Attempts to find a Cookies DB under the temp profile will fail (the `Default/` folder has only `Local Storage`, `Cache`, `History`, etc., no `Cookies`).

This means:
- `rookiepy`, `browser-cookie3`, and direct SQLite queries will ALL fail to find cookies — there's nothing to read
- `document.cookie` in JS only returns non-HttpOnly cookies (missing `__Secure-3PSID`, `HSID`, `SSID` — the critical auth cookies)
- Building `storage_state.json` from JS-visible cookies is insufficient for the CLI

The only reliable way to save cookies for the CLI is Option A in Path B: use a Playwright Python script with the same temp profile path before it gets cleaned up. The user data dir persists as long as the Hermes browser session is alive (Hermes internally reuses the same Playwright context for all browser tool calls within a session).

Tell the user:

> I'm going to open a browser window — just sign into your Google account and navigate to notebooklm.google.com. Take your time, I'll wait for you to confirm before closing it.

Then write and run this login script:

```bash
cat > /tmp/nlm_login.py << 'PYEOF'
import json, os, time
from pathlib import Path
from playwright.sync_api import sync_playwright

STORAGE_PATH = Path.home() / ".notebooklm" / "storage_state.json"
PROFILE_PATH = Path.home() / ".notebooklm" / "browser_profile"
SIGNAL_FILE = Path("/tmp/nlm_save_signal")

SIGNAL_FILE.unlink(missing_ok=True)
STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)

print("Opening browser for Google login...")
print("Sign in to Google and navigate to notebooklm.google.com")

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_PATH),
        headless=False,
        args=["--disable-blink-features=AutomationControlled"],
    )
    page = browser.pages[0] if browser.pages else browser.new_page()
    page.goto("https://notebooklm.google.com/")

    print("Browser is open. Waiting for save signal...")
    while not SIGNAL_FILE.exists():
        time.sleep(1)

    print("Save signal received! Capturing session...")
    storage = browser.storage_state()
    with open(STORAGE_PATH, "w") as f:
        json.dump(storage, f)

    cookie_names = [c["name"] for c in storage.get("cookies", [])]
    print(f"Saved {len(cookie_names)} cookies: {cookie_names}")
    browser.close()

SIGNAL_FILE.unlink(missing_ok=True)
print(f"Authentication saved to: {STORAGE_PATH}")
PYEOF

# Run the login script in the background
source ~/.notebooklm-venv/bin/activate
python3 /tmp/nlm_login.py > /tmp/nlm_login_output.txt 2>&1 &
echo "Login started (PID=$!). Browser should open in a few seconds..."
```

Wait ~10 seconds for the browser to open, then ask the user if they can see the browser and are signed in.

Once the user confirms they are on the NotebookLM homepage, save the session:

```bash
touch /tmp/nlm_save_signal
sleep 8
cat /tmp/nlm_login_output.txt
```

Then verify authentication:

```bash
export PATH="$HOME/bin:$PATH"
notebooklm auth check
notebooklm list
```

If auth passes (SID cookie present), confirm to the user that NotebookLM is set up and ready. Clean up the temp script:

```bash
rm -f /tmp/nlm_login.py /tmp/nlm_login_output.txt /tmp/nlm_save_signal
```

If auth fails (SID cookie missing), the user may not have fully signed in. Delete the browser profile and retry:

```bash
rm -rf ~/.notebooklm/browser_profile ~/.notebooklm/storage_state.json
```

Then run the login script again from the top.

---

## Adding NotebookLM to Co-work

When the user asks to "add this to Co-work", "use this in Co-work", or "make this work in Co-work":

### Step 1: Check auth exists

```bash
cat ~/.notebooklm/storage_state.json > /dev/null 2>&1
```

If it doesn't exist, run the install and authenticate steps above first.

### Step 2: Generate the Co-work skill file

Read the contents of this skill file you are currently using. Then read the contents of `~/.notebooklm/storage_state.json`.

**IMPORTANT — Strip cookies before embedding:** Co-work is sandboxed and can't read local files, so cookies must be inlined. But the full storage_state.json contains duplicate cookies across multiple Google domains (.google.ae, .google.co.uk, .youtube.com, etc.) that are NOT needed. Strip them to save ~55% of tokens.

Run this to generate the minimal auth JSON:
```bash
python3 << 'PYEOF'
import json

with open("$HOME/.notebooklm/storage_state.json") as f:
    data = json.load(f)

# Only these domains are needed for NotebookLM auth
essential_domains = {".google.com", "notebooklm.google.com", "accounts.google.com"}
# Skip analytics/tracking cookies
skip_names = {"_gcl_au", "_ga", "_ga_W0LDH41ZCB", "OTZ", "ACCOUNT_CHOOSER"}

stripped = {
    "cookies": [c for c in data["cookies"] if c["domain"] in essential_domains and c["name"] not in skip_names],
    "origins": [o for o in data.get("origins", []) if "notebooklm" in o.get("origin", "")]
}
print(json.dumps(stripped, separators=(',',':')))
PYEOF
```

Create a MODIFIED copy of this skill file where you replace the entire "Step 0: Setup" section and "Adding NotebookLM to Co-work" section with this:

```markdown
## Auto-Authentication (Co-work)

This skill runs in a sandboxed Co-work environment. Before running ANY notebooklm command, run these setup commands:

\`\`\`bash
pip install notebooklm-py 2>/dev/null
export NOTEBOOKLM_AUTH_JSON='<STRIPPED MINIMAL AUTH JSON FROM ABOVE>'
\`\`\`

Then verify:
\`\`\`bash
notebooklm auth check
notebooklm list
\`\`\`

If auth fails, the cookies may have expired. Ask the user to re-run `notebooklm login` in Claude Code and regenerate this file.
```

### Step 3: Save and instruct

Save the file to the user's Desktop as `NotebookLMSkill-Cowork.md`.

Tell the user:

> Done! I've saved the Co-work skill to your Desktop as `NotebookLMSkill-Cowork.md`. Upload it as a skill in Claude Co-work and you'll have full NotebookLM access there too.
>
> I've stripped the cookies down to only the 21 essential ones (~1,400 tokens instead of ~3,100). When they expire, just come back to Claude Code and say "regenerate my Co-work NotebookLM skill" and I'll make a fresh one.

---

## When This Skill Activates

**Explicit:** User says "/notebooklm", "use notebooklm", "install notebooklm", or mentions the tool by name

**Intent detection:** Recognize requests like:
- "Create a podcast about [topic]"
- "Summarize these URLs/documents"
- "Generate a quiz from my research"
- "Turn this into an audio overview"
- "Create flashcards for studying"
- "Generate a video explainer"
- "Make an infographic"
- "Create a mind map of the concepts"
- "Download the quiz as markdown"
- "Add these sources to NotebookLM"
- "Add this to Co-work" / "Make this work in Co-work"

## Autonomy Rules

**Run automatically (no confirmation):**
- `notebooklm status` - check context
- `notebooklm auth check` - diagnose auth issues
- `notebooklm list` - list notebooks
- `notebooklm source list` - list sources
- `notebooklm artifact list` - list artifacts
- `notebooklm language list` - list supported languages
- `notebooklm language get` - get current language
- `notebooklm language set` - set language (global setting)
- `notebooklm artifact wait` - wait for artifact completion
- `notebooklm source wait` - wait for source processing
- `notebooklm research status` - check research status
- `notebooklm research wait` - wait for research
- `notebooklm use <id>` - set context
- `notebooklm create` - create notebook
- `notebooklm ask "..."` - chat queries (without `--save-as-note`)
- `notebooklm history` - display conversation history (read-only)
- `notebooklm source add` - add sources

**Ask before running:**
- `notebooklm delete` - destructive
- `notebooklm generate *` - long-running, may fail
- `notebooklm download *` - writes to filesystem
- `notebooklm ask "..." --save-as-note` - writes a note
- `notebooklm history --save` - writes a note

## Quick Reference

| Task | Command |
|------|---------|
| List notebooks | `notebooklm list` |
| Create notebook | `notebooklm create "Title"` |
| Set context | `notebooklm use <notebook_id>` |
| Show context | `notebooklm status` |
| Add URL source | `notebooklm source add "https://..."` |
| Add file | `notebooklm source add ./file.pdf` |
| Add YouTube | `notebooklm source add "https://youtube.com/..."` |
| List sources | `notebooklm source list` |
| Wait for source processing | `notebooklm source wait <source_id>` |
| Web research (fast) | `notebooklm source add-research "query"` |
| Web research (deep) | `notebooklm source add-research "query" --mode deep --no-wait` |
| Check research status | `notebooklm research status` |
| Wait for research | `notebooklm research wait --import-all` |
| Chat | `notebooklm ask "question"` |
| Chat (specific sources) | `notebooklm ask "question" -s src_id1 -s src_id2` |
| Chat (with references) | `notebooklm ask "question" --json` |
| Chat (save answer as note) | `notebooklm ask "question" --save-as-note` |
| Show conversation history | `notebooklm history` |
| Save all history as note | `notebooklm history --save` |
| Get source fulltext | `notebooklm source fulltext <source_id>` |
| Generate podcast | `notebooklm generate audio "instructions"` |
| Generate video | `notebooklm generate video "instructions"` |
| Generate report | `notebooklm generate report --format briefing-doc` |
| Generate quiz | `notebooklm generate quiz` |
| Generate flashcards | `notebooklm generate flashcards` |
| Generate infographic | `notebooklm generate infographic` |
| Generate mind map | `notebooklm generate mind-map` |
| Generate slide deck | `notebooklm generate slide-deck` |
| Revise a slide | `notebooklm generate revise-slide "prompt" --artifact <id> --slide 0` |
| Check artifact status | `notebooklm artifact list` |
| Wait for completion | `notebooklm artifact wait <artifact_id>` |
| Download audio | `notebooklm download audio ./output.mp3` |
| Download video | `notebooklm download video ./output.mp4` |
| Download slide deck (PDF) | `notebooklm download slide-deck ./slides.pdf` |
| Download slide deck (PPTX) | `notebooklm download slide-deck ./slides.pptx --format pptx` |
| Download report | `notebooklm download report ./report.md` |
| Download mind map | `notebooklm download mind-map ./map.json` |
| Download data table | `notebooklm download data-table ./data.csv` |
| Download quiz | `notebooklm download quiz quiz.json` |
| Download flashcards | `notebooklm download flashcards cards.json` |
| List languages | `notebooklm language list` |
| Set language | `notebooklm language set zh_Hans` |

## Generation Types

All generate commands support:
- `-s, --source` to use specific source(s) instead of all sources
- `--language` to set output language (defaults to 'en')
- `--json` for machine-readable output
- `--retry N` to automatically retry on rate limits

| Type | Command | Options | Download |
|------|---------|---------|----------|
| Podcast | `generate audio` | `--format [deep-dive\|brief\|critique\|debate]`, `--length [short\|default\|long]` | .mp3 |
| Video | `generate video` | `--format [explainer\|brief]`, `--style [auto\|classic\|whiteboard\|kawaii\|anime\|watercolor\|retro-print\|heritage\|paper-craft]` | .mp4 |
| Slide Deck | generate slide-deck | --format [detailed|presenter], --length [default|short], --append "instructions" (steers content -- frame around a specific project/angle) | .pdf / .pptx |
| Slide Revision | `generate revise-slide "prompt" --artifact <id> --slide N` | `--wait`, `--notebook` | *(re-downloads parent deck)* |
| Infographic | `generate infographic` | `--orientation [landscape\|portrait\|square]`, `--detail [concise\|standard\|detailed]` | .png |
| Report | generate report | --format [briefing-doc|study-guide|blog-post|custom], --append "extra instructions" (steers content -- use this to frame around a specific project instead of letting the AI choose its focus) | .md |
| Mind Map | `generate mind-map` | *(sync, instant)* | .json |
| Data Table | `generate data-table` | description required | .csv |
| Quiz | `generate quiz` | `--difficulty [easy\|medium\|hard]`, `--quantity [fewer\|standard\|more]` | .json/.md/.html |
| Flashcards | `generate flashcards` | `--difficulty [easy\|medium\|hard]`, `--quantity [fewer\|standard\|more]` | .json/.md/.html |

## Common Workflows

### Research to Podcast
1. `notebooklm create "Research: [topic]"`
2. `notebooklm source add` for each URL/document
3. Wait for sources: `notebooklm source list --json` until all status=READY
4. `notebooklm generate audio "Focus on [specific angle]"`
5. Check `notebooklm artifact list` for status
6. `notebooklm download audio ./podcast.mp3` when complete

### Slide Deck to Google Drive
1. `notebooklm create "Presentation: [topic]"`
2. `notebooklm source add ./source.md` (or URLs)
3. Wait for source: `notebooklm source wait <source_id>`
4. `notebooklm generate slide-deck "Detailed instructions — include ALL desired slide wording here to avoid needing revisions later due to rate limits" --format presenter --wait`
5. `notebooklm download slide-deck ./deck.pptx --format pptx`
6. Upload to Drive via OAuth (uses google_token.json refresh token + client_secret.json):
   - Refresh token → new access token
   - `POST https://www.googleapis.com/drive/v3/files` to create folder if needed
   - Multipart upload to target folder

### Research to Slide Deck

When the user asks for a slide deck/presentation from web research:

1. Create a notebook for the topic and set it as context:
   ```bash
   notebooklm create "Topic -- Market Intelligence"
   notebooklm use <notebook_id>
   ```

2. Launch parallel deep research streams (one per dimension of the query):
   ```bash
   notebooklm source add-research "query 1" --mode deep --no-wait
   notebooklm source add-research "query 2" --mode deep --no-wait
   ```

3. Monitor completion with `research status --json`. Avoid calling `research wait --import-all` twice on the same tasks -- it returns "Failed precondition" if already imported. Check `source list` instead.

4. Generate the slide deck with detailed instructions via --append (batch ALL instructions here -- slide revisions have a ~9-per-day quota):
   ```bash
   notebooklm generate slide-deck --wait
   ```
   If `--wait` times out (slide decks take 5-10+ min), check `artifact list` for status and use `artifact wait <id>`.

5. Download both formats:
   ```bash
   notebooklm download slide-deck ./slides.pdf
   notebooklm download slide-deck ./slides.pptx --format pptx
   ```

6. Deliver files to the user. Note: MEDIA: syntax on Discord only handles images (.png, .jpg, .webp) and audio — for PDF/PPTX delivery, use Telegram (MEDIA: works there for all file types) or copy to a file hosting location.

### Fallback: Report → PPTX (when slide deck quota exhausted)

When the initial slide deck daily quota is hit (error: "Slide Deck generation rate limited by Google" at ~0.3s with `--retry` backoffs failing), NotebookLM reports still work:

1. Generate a detailed briefing report instead: `notebooklm generate report --format briefing-doc "detailed instructions" --wait`
2. Download as markdown: `notebooklm download report ./report.md`
3. Convert to PPTX programmatically — pptxgenjs (set `NODE_PATH=/home/linuxbrew/.linuxbrew/lib/node_modules`, dark theme bg:1A1A2E accent:E94560) or python-pptx.
4. Deliver via `MEDIA:/path/to/output.pptx`

**When to use:** After a quota error on `generate slide-deck` that wasn't the first deck. EXPLAIN the rate limit to the user before switching.

### Document Analysis
1. `notebooklm create "Analysis: [project]"`
2. `notebooklm source add ./doc.pdf` (or URLs)
3. `notebooklm ask "Summarize the key points"`
4. Continue chatting as needed

### Research-to-PDF Intelligence Briefing

When you need a formatted PDF briefing document from web research, NotebookLM + weasyPrint produces professional results. This also serves as a **fallback when web_search/web_extract (Firecrawl) is down** — NotebookLM's built-in deep research engine works independently.

**When to use this:** User asks for "deep research on [area] delivered as a PDF/NotebookLM PDF". Or when web_search fails repeatedly with Firecrawl errors — pivot here instead of reporting a blocker.

1. Create a notebook for the topic:
   ```bash
   notebooklm create "Topic — Market Intelligence"
   notebooklm use <notebook_id>
   ```

2. Launch parallel deep research streams covering each dimension of the query:
   ```bash
   notebooklm source add-research "research query 1" --mode deep --no-wait
   notebooklm source add-research "research query 2" --mode deep --no-wait
   ```

3. Wait for all research to complete. Use `research status --json` to monitor — avoid repeated calls to `research wait --import-all` (see pitfall below):
   ```bash
   notebooklm research status --json
   # Check all task statuses are "completed"
   ```

4. Import completed research to the notebook:
   ```bash
   notebooklm research wait --import-all
   ```
   If this returns `Failed precondition`, the tasks were already imported — check `notebooklm source list` to verify sources are present and proceed.

5. Generate a briefing document:
   ```bash
   notebooklm generate report --format briefing-doc --wait
   ```

6. Download as markdown (NotebookLM reports are markdown-only):
   ```bash
   notebooklm download report ./report.md
   ```

7. Convert to styled PDF using weasyPrint (see `references/weasyprint-pdf-conversion.md`):
   - Wrap the markdown content in a dark-themed HTML template
   - Run `weasyprint input.html output.pdf`
   - Deliver via `MEDIA:/path/to/output.pdf`

**Key differences from web_search:** NotebookLM deep research returns richer, multi-source reports with embedded citations and often finds sources that web_search misses. However, it runs asynchronously (takes 1-3 min per query) vs web_search's instant results. Use NotebookLM for depth, web_search for speed.

## Output Formats (--json)

```json
// notebooklm list --json
{"notebooks": [{"id": "...", "title": "...", "created_at": "..."}]}

// notebooklm source list --json
{"sources": [{"id": "...", "title": "...", "status": "ready|processing|error"}]}

// notebooklm artifact list --json
{"artifacts": [{"id": "...", "title": "...", "type": "Audio Overview", "status": "in_progress|pending|completed|unknown"}]}
```

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| Auth/cookie error | Session expired | Re-run `notebooklm login` |
| "No notebook context" | Context not set | Run `notebooklm use <id>` |
| Rate limiting (generation) | Google transient throttle | Wait 5-10 min, retry; `--retry N` works |
| Rate limiting (slide deck generation) | Google daily quota (separate from revisions) | Initial slide deck generation has ~1-2 per day quota per notebook. If the first succeeds and a second attempt fails at 0.4s with \"Slide Deck generation rate limited\", the daily quota is exhausted. `--retry N` waits 60s/120s/240s but won't bypass it. Workaround: if you need a second deck from the same notebook, use pptxgenjs or python-pptx as a fallback — but EXPLAIN the rate limit to the user first. |
| Download fails | Generation incomplete | Check `artifact list` for status |
| `RPC [...] returned null result with status code 9 (Failed precondition)` | `research wait --import-all` retried on already-imported tasks | Check `source list` — sources are already present. Ignore the error or import individual tasks by ID. |
| Slide deck --wait times out (>300s) | Generation takes longer than default | Don't retry `generate slide-deck --wait` — the generation is still running server-side. Use `artifact list --json`, find the in_progress artifact ID, then `artifact wait <id>` to block until completion. |

## Known Limitations

- Audio, video, quiz, flashcard, infographic, and slide deck generation may fail due to Google rate limits
- Slide revision (`revise-slide`) has a harder daily quota: ~9 revisions per session before being locked out for 1-24h. Batch corrections into the original `generate slide-deck` prompt when possible
- Generation times: audio 10-20 min, video 15-45 min, quiz/flashcards 5-15 min, slide deck 5-10+ min (--wait often times out at 300s -- use `artifact list` + `artifact wait <id>` as fallback)
- This is an unofficial API — Google can change things without warning
