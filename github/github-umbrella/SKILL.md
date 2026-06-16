---
name: github-umbrella
description: GitHub workflow orchestration — PR lifecycle, code review, repo management, authentication, and issues. Use when working with GitHub repos, pull requests, or GitHub API.
category: github
---

# GitHub Workflows

Orchestrates the complete GitHub lifecycle — authentication, repository management, pull requests, code review, and issues.

### Absorbed Skills (use subsections below)

> **Note:** For any GitHub data query (commits, issues, PRs, repos, file contents), use `gh api` with `--jq` FIRST — before web search or web_extract. See `references/github-cli-first.md` for patterns and examples.

### github-auth
Handles: HTTPS tokens, SSH keys, gh CLI login, repo access setup.
```bash
gh auth login --with-token <token>
gh auth setup-git
```

### github-pr-workflow
Handles: branch creation, commits, PR opening, CI checks, merging.
```bash
gh repo clone owner/repo
git checkout -b feature-branch
gh pr create --title "feat: description" --body "Details"
gh pr merge --squash
```

### github-code-review
Handles: reviewing PRs, inline comments, approving, requesting changes.
```bash
gh pr review <pr-number> --comment --body "Review notes"
gh pr review <pr-number> --approve
```

### github-repo-management
Handles: creating repos, managing remotes, releases, fork sync.
```bash
gh repo create name [--private|--public]
gh repo clone owner/repo
gh release create v1.0.0 --notes "Release notes"
```

### github-issues
Handles: creating, labeling, assigning, closing issues via gh or REST.
```bash
gh issue create --title "Bug: description" --body "Steps"
gh issue edit <number> --label bug --assignee @me
```

### codebase-inspection
Handles: LOC counting, language analysis, repo stats via pygount.
```bash
pygount --format xml,out.csv .
```

## Reference Files
- `references/github-cli-first.md` — gh CLI patterns for commits, issues, PRs, files (always prefer gh over web for GitHub data)
- `references/github-api-rate-limits.md` — API rate limit handling
- `references/ssh-vs-https.md` — Auth method differences
