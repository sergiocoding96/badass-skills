# badass-skills
My collection of Claude Code / Hermes Agent skills.
**15 skills** — synced automatically from `~/.hermes/skills/`

## Skills

| Skill | Category | Description |
|-------|----------|-------------|
| [.git](./.git/) | — | — |
| [daily-tech-briefing](./daily-tech-briefing/) | research | Daily AI/Tech intelligence briefing — aggregates blogs, GitHub, YouTube, and X into a consolidated report delivered via Telegram |
| [debugging-and-preparing-to-run-e2e-test-for-openclaw-video-skill-pipeline](./debugging-and-preparing-to-run-e2e-test-for-openclaw-video-skill-pipeline/) | — | "Debugging and Preparing to Run E2E Test for OpenClaw Video Skill Pipeline in Cursor. Generated from live Screenpipe capture." |
| [debugging-invalid-gemini-api-key-in-openclaw-video-skill-pipeline](./debugging-invalid-gemini-api-key-in-openclaw-video-skill-pipeline/) | — | "Debugging Invalid Gemini API Key in openclaw-video-skill-pipeline in Cursor.exe. Generated from live Screenpipe capture." |
| [devops-github-cli-first](./devops-github-cli-first/) | — | Use gh CLI as first resort for GitHub data — commits, issues, PRs, repos. Only fall back to web_search/web_extract when gh can't do the job. |
| [dogfood](./dogfood/) | — | "Exploratory QA of web apps: find bugs, evidence, reports." |
| [gemini-video](./gemini-video/) | — | Download a video from a Vimeo (or YouTube) URL and analyze it with Google Gemini's multimodal vision. Returns a structured analysis covering content summary, key moments, speakers, and custom insights. |
| [hermes-devops](./hermes-devops/) | devops | Complete Hermes infrastructure operations — disk space recovery, emergency cleanup, Firecrawl recovery, web stack setup, system health checks, and Tailscale funnel management. Use when disk is critically full (≥95%), services are unreachable, or diagnosing infrastructure failures. |
| [hermes-mlops-inference](./hermes-mlops-inference/) | mlops/inference | Complete LLM inference workflows — serving with vLLM, GGUF quantization for CPU/GPU, structured output with Outlines and Guidance, and model surgery (ablation/removal of refusal layers). Use when serving LLMs, quantizing models, or extracting/ablating model layers. |
| [hermes-mlops-training](./hermes-mlops-training/) | mlops/training | Complete LLM fine-tuning and training workflows for Hermes — LoRA/QLoRA via axolotl, RL training via TRL (GRPO/DPO/SFTTrainer), distributed training via PyTorch FSDP, and fast fine-tuning via Unsloth. Use when fine-tuning an LLM, setting up RLHF training, or configuring distributed training infrastructure. |
| [notebooklm](./notebooklm/) | — | Complete API for Google NotebookLM - full programmatic access including features not in the web UI. Create notebooks, add sources, generate all artifact types, download in multiple formats. Activates on explicit /notebooklm or intent like "create a podcast about X", "install notebooklm", "add notebooklm to cowork" |
| [pdf](./pdf/) | — | Extract text from PDFs with automatic OCR fallback. Use when user wants to read a PDF, extract text from a PDF, or convert PDF to text. |
| [repo-sync-workflow](./repo-sync-workflow/) | autonomous-ai-agents | Sync skills from local ~/.hermes/skills/ to the sergiocoding96/badass-skills GitHub repo. Use when Sergio asks to sync/update/repo the skills, or when the local repo diverges significantly from the GitHub source. The openclaw-sync cron only handles repo→local direction — this skill handles the reverse. |
| [testing-text-input-and-word-count-on-online-notepad](./testing-text-input-and-word-count-on-online-notepad/) | — | "Testing Text Input and Word Count on Online Notepad in Google Chrome. Generated from live Screenpipe capture." |
| [yuanbao](./yuanbao/) | — | "Yuanbao (元宝) groups: @mention users, query info/members." |
