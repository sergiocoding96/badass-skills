---
name: gemini-video
description: Download a video from a Vimeo (or YouTube) URL and analyze it with Google Gemini's multimodal vision. Returns a structured analysis covering content summary, key moments, speakers, and custom insights.
argument-hint: <vimeo-or-youtube-url> [--prompt "custom question"] [--mode summary|transcript|insights]
---

# Gemini Video Analysis Skill

Download a video from Vimeo or YouTube and analyze it using Google Gemini multimodal AI.

## Usage

```
/gemini-video <url> [--prompt "your question"] [--mode summary|transcript|insights]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `<url>` | Yes | Vimeo or YouTube URL |
| `--prompt "..."` | No | Custom analysis question for Gemini |
| `--mode` | No | `summary` (default), `transcript`, or `insights` |

## How It Works

1. **Install yt-dlp** if not present
2. **Download video** to a temp file (best quality ≤ 720p to stay within Gemini limits)
3. **Upload to Gemini Files API** and wait for processing
4. **Analyze** with Gemini 2.0 Flash using the selected mode or custom prompt
5. **Return** structured insights and clean up temp file

---

## Execution Instructions

When this skill is invoked, follow these steps exactly:

### Step 1 — Parse arguments

Extract from `$ARGUMENTS`:
- `URL`: the first non-flag argument (Vimeo/YouTube link)
- `PROMPT`: value after `--prompt` (if present)
- `MODE`: value after `--mode` (default: `summary`)

If no URL is provided, stop and ask: "Please provide a Vimeo or YouTube URL."

### Step 2 — Check and install yt-dlp

```bash
python -m yt_dlp --version
```

If not found:
```bash
pip install yt-dlp
```

> On Windows, use `python -m yt_dlp` instead of `yt-dlp` throughout.

### Step 3 — Check for GEMINI_API_KEY

Check if `GEMINI_API_KEY` environment variable is set:
```bash
python -c "import os; print('OK' if os.environ.get('GEMINI_API_KEY') else 'MISSING')"
```

If MISSING, also check for `GOOGLE_API_KEY`. If neither found, stop and tell the user:
> Set your Gemini API key: `export GEMINI_API_KEY=your_key_here`
> Get one free at https://aistudio.google.com/apikey

### Step 4 — Download the video

```bash
python -m yt_dlp -f "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]" \
  --merge-output-format mp4 \
  -o "/tmp/gemini_video_%(id)s.%(ext)s" \
  --no-playlist \
  "<URL>"
```

Capture the output filename. If download fails with a permissions error (private/password-protected Vimeo), tell the user:
> This video is private or requires a Vimeo login. Try: `yt-dlp --cookies-from-browser chrome <url>`

### Step 5 — Build the analysis prompt

Based on MODE:

**summary** (default):
```
Analyze this video and provide:
1. **Overview** — What is this video about? (2-3 sentences)
2. **Key Topics** — Main subjects covered (bullet list)
3. **Key Moments** — Notable timestamps with descriptions
4. **Speakers/People** — Who appears or speaks (if identifiable)
5. **Takeaways** — Most important insights or conclusions
```

**transcript**:
```
Provide a detailed transcript of all speech in this video, formatted with approximate timestamps. Include speaker labels if multiple people are speaking.
```

**insights**:
```
Watch this video from a business/strategic perspective and provide:
1. **Business Context** — What business problem or opportunity is being discussed?
2. **Key Decisions or Actions** — What decisions, commitments, or next steps are mentioned?
3. **People & Roles** — Who is involved and what are their roles?
4. **Financial or Commercial Signals** — Any mentions of numbers, pricing, budgets, timelines?
5. **Follow-up Recommendations** — What should be done after watching this?
```

If `--prompt` was provided, use that prompt directly instead of the above templates.

### Step 6 — Run Gemini analysis

Write and execute this Python script:

```python
import google.generativeai as genai
import os
import time
import sys

api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=api_key)

video_path = sys.argv[1]
prompt = sys.argv[2]

print(f"Uploading video ({os.path.getsize(video_path) / 1024 / 1024:.1f} MB)...")
video_file = genai.upload_file(path=video_path, mime_type="video/mp4")

print("Waiting for Gemini to process video...")
while video_file.state.name == "PROCESSING":
    time.sleep(3)
    video_file = genai.get_file(video_file.name)

if video_file.state.name == "FAILED":
    print("ERROR: Gemini failed to process the video.")
    sys.exit(1)

print("Analyzing with Gemini...\n")
model = genai.GenerativeModel("gemini-2.0-flash")
response = model.generate_content([video_file, prompt])
print(response.text)

# Cleanup
genai.delete_file(video_file.name)
print("\n[Gemini file deleted from cloud]")
```

Run as:
```bash
python /tmp/gemini_analyze.py "<video_path>" "<prompt>"
```

### Step 7 — Clean up and present results

Delete the local video file:
```bash
rm "/tmp/gemini_video_*.mp4"
```

Present the Gemini response in a clean, readable format with a header showing:
- Video URL
- Analysis mode used
- Model: gemini-2.0-flash

### Error handling

| Error | Response |
|-------|----------|
| Video too large (>2GB) | Use `--format "worst"` flag to get smaller file |
| Vimeo private video | Suggest `--cookies-from-browser chrome` |
| API quota exceeded | Tell user to check quota at aistudio.google.com |
| Unsupported format | Convert with `ffmpeg -i input.webm output.mp4` |
