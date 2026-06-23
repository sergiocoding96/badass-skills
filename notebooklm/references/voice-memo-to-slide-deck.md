# Voice Memo → NotebookLM Multi-Format Presentation Pipeline

Convert an audio voice memo (recap, team sync, client update, strategy session) into a structured NotebookLM multi-format presentation: slide deck + briefing report + audio podcast.

## Workflow

### Step 1: Transcribe

Transcribe the audio first. Use Deepgram Nova-3 via curl (most reliable with the key in `~/.hermes/profiles/sergio/.env`):

```bash
DEEPGRAM_KEY=$(grep DEEPGRAM_API_KEY ~/.hermes/profiles/sergio/.env | head -1 | sed 's/DEEPGRAM_API_KEY=//' | xargs)

curl -s -X POST "https://api.deepgram.com/v1/listen?model=nova-3&language=en&smart_format=true&punctuate=true&paragraphs=true" \
  -H "Authorization: Token $DEEPGRAM_KEY" \
  -H "Content-Type: audio/mpeg" \
  --data-binary @/path/to/audio.mp3 \
  -o /tmp/dg_response.json

# Extract transcript
python3 -c "import json; d=json.load(open('/tmp/dg_response.json')); print(d['results']['channels'][0]['alternatives'][0]['transcript'])"
```

**Note:** Deepgram SDK v7's Python API changed significantly — the `DeepgramClient` class is available but the old `PrerecordedOptions` import no longer works. Using curl directly is simpler and more reliable.

### Step 2: Structure & Save

Save the transcript as a structured markdown file in `memory/YYYY-MM-DD.md` with sections:
- 🎉 Celebrations
- 🔄 Strategic changes
- 🎯 Vision / Direction
- 📋 Client feedback
- ✅ Action plans (per person)

This file doubles as both the daily memory note AND the NotebookLM source.

### Step 3: Create Notebook & Add Source

```bash
notebooklm create "Title — Description"
notebooklm use <notebook_id>
notebooklm source add ./memory/YYYY-MM-DD.md
notebooklm source wait <source_id>
```

### Step 4: Multi-Artifact Generation (Recommended)

Generate multiple artifact types from the same source for a comprehensive output. All can run in parallel — NotebookLM handles concurrent generation of different artifact types from the same notebook.

```bash
# All three can fire immediately — they run independently
notebooklm generate slide-deck \
  --format detailed \
  "Create a comprehensive presentation covering: [slide-by-slide outline with all key content, celebrations, action items]"

notebooklm generate report \
  --format briefing-doc \
  "Create a comprehensive briefing document covering: [key topics, decisions, team tasks, action items]"

notebooklm generate audio \
  "[instructions for podcast tone and content — e.g. energetic team huddle, focused strategy session, client update]"
```

All three return artifact IDs immediately. Track and wait on each:

```bash
# Check all artifacts
notebooklm artifact list --json

# Wait for each (they complete at different speeds: report fastest, then slide deck, then audio slowest)
notebooklm artifact wait <report_id>
notebooklm artifact wait <slide_deck_id>
notebooklm artifact wait <audio_id>
```

**Timing expectations from real runs:**
- **Briefing report**: ~2-5 min (fastest)
- **Slide deck**: ~5-10 min
- **Audio podcast**: ~8-20 min (may transition through "pending" status — this is Google's queue, wait continues)
- **Video explainer**: ~15-45 min (slowest)

### Step 5: Handle `--wait` Timeout

`--wait` times out at 300s for slide decks. **Don't use `--wait` for slide-deck generation** — it always times out. Instead launch without `--wait` (returns artifact ID immediately) and poll with `artifact wait`:

```bash
notebooklm generate slide-deck "instructions"  # Returns artifact ID immediately
notebooklm artifact list --json                 # Check status
notebooklm artifact wait <id>                   # Blocks until completion
```

This pattern also works for audio (podcasts) — `--wait` will also time out at 300s on audio, but `artifact wait` will properly wait for the full 10-20 min.

### Step 6: Download All Artifacts

```bash
# Slide deck — download both formats
notebooklm download slide-deck ./output.pptx --format pptx
notebooklm download slide-deck ./output.pdf

# Briefing report
notebooklm download report ./output.md

# Audio podcast
notebooklm download audio ./output.mp3

# Video (if generated)
notebooklm download video ./output.mp4
```

Deliver via `MEDIA:/path/to/output.pptx`, `MEDIA:/path/to/output.pdf`, `MEDIA:/path/to/output.mp3`, etc. Telegram handles all file types natively.

## Pitfalls

- **`--append` doesn't exist for slide-deck** — the skill's Generation Types table previously documented this flag. Always pass instructions as the DESCRIPTION positional argument.
- **`generate slide-deck` without description may fail** with `"no artifact_id returned"` if NotebookLM can't determine what to generate. Always include a description/instructions.
- **`--wait` times out at 300s** — the generation is still running server-side. Use `artifact list` + `artifact wait <id>` to check completion.
- **Daily quota**: ~1-2 slide decks per notebook per day. Batch all instructions into one generation to avoid needing quota-costly slide revisions.
- **Audio can show "pending" status**: Unlike reports and slide decks which go straight to "in_progress", audio podcast generation may enter a "pending" queue state (status_id: 2) before transitioning to "in_progress" (1) → "completed" (3). This is normal — `artifact wait <id>` handles it correctly, just takes longer (~8-20 min total). Don't retry if it shows "pending".
- **audio `--wait` also times out at 300s**: Same as slide decks. Launch without `--wait`, record the artifact ID, use `artifact wait <id>` to block until full completion.
- **Slide deck title may differ from notebook title**: NotebookLM may auto-title the slide deck artifact differently from the notebook title (e.g. notebook titled "Team Strategy" produces deck titled "AI Real Estate Blueprint"). Don't rely on artifact title matching — use the artifact ID from the generate response.
