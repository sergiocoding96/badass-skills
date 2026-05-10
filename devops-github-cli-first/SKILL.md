---
name: github-cli-first
description: Use gh CLI as first resort for GitHub data — commits, issues, PRs, repos. Only fall back to web_search/web_extract when gh can't do the job.
version: 0.1.0
platforms:
  - linux
  - macos
metadata:
  hermes:
    tags: [github, gh-cli]
---

# GitHub CLI First

Always use `gh` CLI before web search or web extract for GitHub data.

## Why

- **Clean structured output** — `gh api` with `--jq` returns clean JSON, no page rendering mess
- **Faster** — direct API call vs scraping HTML
- **Authenticated** — respects your GitHub auth, sees private repos you're authorized for

## Common Commands

```bash
# Recent commits with one-line message, date, author
gh api repos/{owner}/{repo}/commits --jq '.[0:20] | .[] | {sha: .sha[0:7], msg: .commit.message | split("\n")[0], date: .commit.author.date, author: .author.login}'

# Issues (open, recent)
gh api repos/{owner}/{repo}/issues --jq '.[] | {number, title, state, created: .created_at}'

# PRs (open, with labels)
gh api repos/{owner}/{repo}/pulls --jq '.[] | {number, title, state, labels: .labels[].name}'

# Repo info
gh repo view {owner}/{repo} --json description,stargazer_count,forkCount,default_branch

# File contents (any branch/ref)
gh api repos/{owner}/{repo}/contents/{path} --jq '.content' -H "Accept: application/vnd.github+json"

# Search repos
gh search repos "hermes multi-agent" --owner sergiocoding96

# Check rate limit
gh api rate_limit
```

## jq Tips

- `.sha[0:7]` — truncate SHA to 7 chars
- `.commit.message | split("\n")[0]` — first line only (subject)
- `select(.state == "open")` — filter
- `map({x, y})` — reshape objects
- `.[]` — iterate arrays

## When to Fall Back to Web

- **GitHub UI features** — code search, code browsing, file explorer rendering
- **GitHub Actions / CI logs** — need UI access
- **Large README rendering** — sometimes web_extract works but `gh api contents/README.md` is cleaner
- **Search across code** — `gh search code` requires authenticated limits; web search may be faster for broad queries

## Gotcha

If `gh` returns empty results, check:
1. `gh auth status` — are you logged in?
2. `gh api rate_limit` — hitting rate limits?
3. Repo is private → you need `repo` scope: `gh auth refresh --scope repo`