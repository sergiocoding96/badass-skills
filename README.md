# badass-skills

My collection of Claude Code skills. Install any skill by copying its `SKILL.md` into `~/.claude/skills/<skill-name>/`.

## Skills

| Skill | Description |
|-------|-------------|
| [gemini-video](./gemini-video/) | Analyze videos with Google Gemini multimodal vision |
| [notebooklm](./notebooklm/) | Full programmatic access to Google NotebookLM — notebooks, sources, podcasts, videos, slides, and more |
| [pdf](./pdf/) | Extract text from PDFs with automatic OCR fallback |

## Quick Install

```bash
# Clone and symlink a skill
git clone https://github.com/sergiocoding96/badass-skills.git
cp -r badass-skills/<skill-name> ~/.claude/skills/<skill-name>
```
