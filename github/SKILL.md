---
name: github
description: "One stop for every GitHub operation: auth, issues, PRs, code review, repo management, CI/CD, releases, secrets, and Actions. Merges github-auth, github-code-review, github-issues, github-pr-workflow, and github-repo-management."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Pull-Requests, Issues, Code-Review, CI/CD, Repositories, Releases, Actions, git, gh]
    related_skills: []
---

# GitHub — Complete Operations Umbrella

Single skill covering every GitHub operation. Shared auth detection at the top; then labeled sections for each domain. Detailed workflows live in `references/`; templates in `templates/`.

---

## Shared Prerequisites (all sections)

Run this once at the start of any GitHub workflow:

```bash
# Auth detection
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="curl"
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi

# Extract owner/repo
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)

echo "Auth: $AUTH | Repo: $OWNER/$REPO"
```

Helper script: source `scripts/gh-env.sh` to set `GH_AUTH_METHOD`, `GITHUB_TOKEN`, `GH_USER`, `GH_OWNER`, `GH_REPO` in one call.

---

## A: Authentication Setup

Two paths. Run the detection block above first.

### gh CLI (Simplest)

```bash
gh auth login           # interactive browser
echo "$TOKEN" | gh auth login --with-token   # headless
gh auth setup-git       # propagate to git
gh auth status          # verify
```

### Git + Token (No gh)

```bash
# HTTPS with credential helper
git config --global credential.helper store
git config --global user.name "Your Name"
git config --global user.email "email@example.com"

# Use token as password on first git operation
# Or embed directly:
git remote set-url origin https://$USER:$TOKEN@github.com/$OWNER/$REPO.git
```

### SSH Keys

```bash
ssh-keygen -t ed25519 -C "email@example.com" -f ~/.ssh/id_ed25519 -N ""
cat ~/.ssh/id_ed25519.pub    # add to https://github.com/settings/keys
ssh -T git@github.com        # verify
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

---

## B: Repository Management

### Clone

```bash
git clone https://github.com/owner/repo.git
gh repo clone owner/repo
```

### Create

```bash
# gh
gh repo create my-project --public --clone

# curl
curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user/repos \
  -d '{"name": "my-project", "private": false, "auto_init": true}'
```

### Fork & Sync

```bash
gh repo fork owner/repo --clone
git remote add upstream https://github.com/owner/repo.git
git fetch upstream && git merge upstream/main && git push origin main
```

### Releases

```bash
gh release create v1.0.0 --title "v1.0.0" --generate-notes
gh release list
gh release download v1.0.0 --dir ./downloads
```

### Secrets

```bash
gh secret set API_KEY --body "value"
gh secret list
gh secret delete API_KEY
```

### Branch Protection

```bash
curl -s -X PUT -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/branches/main/protection \
  -d '{"required_status_checks": {"strict": true, "contexts": ["ci/test"]}, "required_pull_request_reviews": {"required_approving_review_count": 1}}'
```

### Gists

```bash
gh gist create script.py --public --desc "Description"
```

**Reference:** `references/github-api-cheatsheet.md` (full REST API endpoint table)  
**Reference:** `references/codebase-inspection-pygount.md` (LOC and language breakdown)

---

## C: Issues Management

### View

```bash
gh issue list
gh issue list --state open --label "bug"
gh issue view 42
```

### Create

```bash
gh issue create --title "Bug: login redirect" \
  --body "## Description\n..." --label "bug" --assignee "@me"
```

### Manage

```bash
gh issue edit 42 --add-label "priority:high" --add-assignee username
gh issue comment 42 --body "Working on this."
gh issue close 42 --reason "completed"
gh issue reopen 42
```

**Templates:** `templates/bug-report.md`, `templates/feature-request.md`

### Triage Workflow

1. List untriaged: `gh issue list --label "needs-triage" --state open`
2. Read each issue (view details)
3. Apply labels and assignment
4. Comment with triage notes

### Bulk Operations

```bash
# Close all issues with a specific label
gh issue list --label "wontfix" --json number --jq '.[].number' | \
  xargs -I {} gh issue close {} --reason "not planned"
```

---

## D: Pull Request Workflow

### Branch & Commit

```bash
git checkout -b feat/add-auth
git add src/
git commit -m "feat: add JWT authentication"
git push -u origin HEAD
```

**Reference:** `references/conventional-commits.md` (commit message types & conventions)

### Create PR

```bash
gh pr create --title "feat: add auth" \
  --body "## Summary\nCloses #42" \
  --label "enhancement" --reviewer @me
```

**Templates:** `templates/pr-body-feature.md`, `templates/pr-body-bugfix.md`

### Monitor CI

```bash
gh pr checks
gh pr checks --watch                          # poll until done
gh run list --branch $(git branch --show-current) --limit 5
```

### Auto-Fix CI Loop

1. Check CI status → identify failures
2. Read logs: `gh run view <ID> --log-failed` (or download via curl)
3. Fix code → `git commit -m "fix: ..." && git push`
4. Re-check; repeat up to 3x, then escalate

**Reference:** `references/ci-troubleshooting.md` (common failure patterns)

### Merge

```bash
gh pr merge --squash --delete-branch
gh pr merge --auto --squash --delete-branch    # merge when CI passes
```

---

## E: Code Review

### Review Local Changes (Pre-Push)

```bash
git diff main...HEAD --stat
git diff main...HEAD
git diff main...HEAD | grep -n "print(\|TODO\|FIXME\|debugger"   # problem scan
```

### Review a GitHub PR

```bash
gh pr view 123
gh pr diff 123 --name-only
gh pr checkout 123
```

### Submit Formal Review

```bash
gh pr review 123 --approve --body "LGTM!"
gh pr review 123 --request-changes --body "See inline comments."
```

### Review Checklist

- **Correctness:** edge cases, error paths, null handling
- **Security:** hardcoded secrets, SQL injection, XSS, path traversal, eval()
- **Quality:** naming, DRY, single responsibility, no dead code
- **Testing:** new paths covered with regression tests
- **Performance:** N+1 queries, blocking calls in async code

**Template:** `references/review-output-template.md` (structured output format)

---

## F: GitHub Actions

```bash
gh workflow list
gh run list --limit 10
gh run view <RUN_ID> --log-failed
gh run rerun <RUN_ID>
gh run rerun <RUN_ID> --failed
gh workflow run ci.yml --ref main
```

---

## Quick Reference Table

| Action | gh command | curl endpoint |
|--------|-----------|---------------|
| Clone repo | `gh repo clone o/r` | `git clone https://github.com/o/r.git` |
| Create repo | `gh repo create name --public` | `POST /user/repos` |
| Fork | `gh repo fork o/r --clone` | `POST /repos/o/r/forks` |
| List issues | `gh issue list` | `GET /repos/{o}/{r}/issues` |
| Create issue | `gh issue create ...` | `POST /repos/{o}/{r}/issues` |
| Add labels | `gh issue edit N --add-label ...` | `POST /repos/{o}/{r}/issues/N/labels` |
| Create PR | `gh pr create ...` | `POST /repos/{o}/{r}/pulls` |
| Merge PR | `gh pr merge --squash` | `PUT /repos/{o}/{r}/pulls/N/merge` |
| Submit review | `gh pr review N --approve` | `POST /repos/{o}/{r}/pulls/N/reviews` |
| List workflows | `gh workflow list` | `GET /repos/{o}/{r}/actions/workflows` |
| Rerun CI | `gh run rerun N` | `POST /repos/{o}/{r}/actions/runs/N/rerun` |
| Set secret | `gh secret set KEY` | `PUT /repos/{o}/{r}/actions/secrets/KEY` |
| Create release | `gh release create v1.0` | `POST /repos/{o}/{r}/releases` |

---

## Pitfalls

1. **Auth block first** — Always run the shared auth detection at the start of any workflow. Every sub-skill had the same 15-line auth block duplicated; the umbrella eliminates that.
2. **`gh pr checks` needs the PR checked out** — If you're not on the PR branch, run `gh pr checkout N` first.
3. **`gh issue list` returns PRs too** — Filter with `'pull_request' not in item` when parsing curl JSON.
4. **Secrets need encryption** — `gh secret set` is simple; curl requires libsodium + public key. Prefer `gh`.
5. **Auto-merge needs GraphQL** — REST doesn't support it. Use `gh pr merge --auto` or GraphQL.
6. **PR/issue numbers share the same counter** — #42 is either an issue or a PR.
