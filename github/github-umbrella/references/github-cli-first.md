# gh CLI First — GitHub Data Queries

**Rule:** For any GitHub data (commits, issues, PRs, file contents, repo info), use `gh api` with `--jq` before web search or web_extract.

## Why

- Clean structured JSON output — no HTML rendering mess
- Faster — direct API call
- Authenticated — respects your GitHub auth, accesses private repos

## Commit History

```bash
# Recent commits (sha truncated to 7, first line of msg, date, author)
gh api repos/{owner}/{repo}/commits --jq '.[0:20] | .[] | {sha: .sha[0:7], msg: .commit.message | split("\n")[0], date: .commit.author.date, author: .author.login}'

# All branches
gh api repos/{owner}/{repo}/commits --jq '.[] | .sha' -H "Accept: application/vnd.github+json"

# Single commit
gh api repos/{owner}/{repo}/commits/{sha} --jq '{msg: .commit.message, author: .author.name, date: .commit.author.date}'
```

## Issues

```bash
# Open issues
gh api repos/{owner}/{repo}/issues --jq '.[] | {number, title, state, created: .created_at} | select(.state=="open")'

# Recent issues
gh api repos/{owner}/{repo}/issues --jq 'sort_by(.created_at) | reverse | .[0:10]'
```

## Pull Requests

```bash
# Open PRs
gh api repos/{owner}/{repo}/pulls --jq '.[] | {number, title, state, labels: .labels[].name}'

# PR diff
gh api repos/{owner}/{repo}/pulls/{number} --jq '.body'
```

## File Contents

```bash
# README or any file
gh api repos/{owner}/{repo}/contents/{path} --jq '.content' -H "Accept: application/vnd.github+json" | base64 -d

# Directory listing
gh api repos/{owner}/{repo}/contents/{path} --jq '.[].name'
```

## Repo Info

```bash
gh repo view {owner}/{repo} --json description,stargazer_count,forkCount,default_branch
```

## Search

```bash
# Repos by owner
gh search repos "hermes multi-agent" --owner sergiocoding96

# Code
gh search code "hermes_chat" --owner nousresearch
```

## jq Tricks

| Expression | Effect |
|------------|--------|
| `.sha[0:7]` | Truncate SHA |
| `.commit.message \| split("\n")[0]` | First line only |
| `select(.state == "open")` | Filter |
| `map({x, y})` | Reshape objects |
| `.[]` | Iterate |

## Troubleshooting

```bash
# Check auth
gh auth status

# Check rate limit
gh api rate_limit

# Private repo needs scope
gh auth refresh --scope repo
```

## When to Fall Back

- GitHub UI features (code browsing, file explorer)
- GitHub Actions / CI logs
- Large README rendering (web_extract can handle better)
- Search across code (web search may be faster for broad queries)