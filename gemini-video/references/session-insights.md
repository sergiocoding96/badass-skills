# Gemini Video Analysis — Session-Specific Notes

## Key Insights from Sessions

### Video Size Limits
- Gemini 2.0 Flash accepts videos up to 2GB
- Best results with ≤720p — use `--format "best[height<=720]"`
- Very large videos (>2GB) get rejected with a size error

### Vimeo Private Videos
- yt-dlp cannot download private Vimeo videos without authentication
- If cookie-based auth fails, the video is inaccessible via API
- Workaround: Use `--cookies-from-browser chrome` for personal account access

### Gemini Processing Time
- Videos take 10-30 seconds to process after upload
- Processing is async — poll `video_file.state.name` until PROCESSING completes
- If state becomes FAILED, retry once before giving up

### API Key Precedence
```python
# Check both, prefer GEMINI_API_KEY
api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
```
