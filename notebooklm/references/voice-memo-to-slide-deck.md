# Voice Memo → NotebookLM Slide Deck Pipeline

Convert an audio voice memo (recap, team sync, client update) into a structured NotebookLM slide deck.

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

### Step 4: Generate Slide Deck

Pass ALL instructions as the DESCRIPTION positional argument (not `--append` — that flag doesn't exist for `generate slide-deck`):

```bash
notebooklm generate slide-deck \
  --format detailed \
  "Create a comprehensive presentation covering: [slide-by-slide outline with all key content, celebrations, action items]"
```

### Step 5: Handle `--wait` Timeout

`--wait` times out at 300s for slide decks. The generation continues server-side. Check with:

```bash
notebooklm artifact list --json
# Find the artifact ID with status "completed"
notebooklm artifact wait <artifact_id>
```

Alternatively, skip `--wait` entirely and poll manually:
```bash
notebooklm generate slide-deck "instructions"  # Returns artifact ID immediately
notebooklm artifact wait <id>                   # Blocks until completion
```

### Step 6: Download

```bash
notebooklm download slide-deck ./output.pptx --format pptx
notebooklm download slide-deck ./output.pdf
```

Deliver via `MEDIA:/path/to/output.pptx` and `MEDIA:/path/to/output.pdf`.

## Pitfalls

- **`--append` doesn't exist for slide-deck** — the skill's Generation Types table previously documented this flag. Always pass instructions as the DESCRIPTION positional argument.
- **`generate slide-deck` without description may fail** with `"no artifact_id returned"` if NotebookLM can't determine what to generate. Always include a description/instructions.
- **`--wait` times out at 300s** — the generation is still running server-side. Use `artifact list` + `artifact wait <id>` to check completion.
- **Daily quota**: ~1-2 slide decks per notebook per day. Batch all instructions into one generation to avoid needing quota-costly slide revisions.
