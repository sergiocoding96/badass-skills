---
name: source-github
description: Check GitHub trending repos in AI/ML topics for daily briefing
category: research
---

# Source: GitHub Trending

Monitor GitHub trending repositories in AI/ML topics.

## Target Topics
- ai
- machine-learning
- llm
- ai-agents
- gpt
- openai
- autonomous-agents

## GitHub API
```
GET https://api.github.com/search/repositories
  ?q=topic:ai+created:>2024-01-01
  &sort=stars
  &order=desc
  &per_page=20
```

Or use GitHub trending page: `https://github.com/trending?l=python&since=daily`

## Data to Extract
- Repo name and owner
- Description
- Primary language
- Star count (today/this week)
- URL
- What problem it solves
- Business/application potential

## Filtering
- Focus on repos that could be used as products or services
- AI tools, agents, automation libraries
- Anything with clear business use cases
- Skip pure research papers unless game-changing

## Output Format
```json
[
  {
    "name": "owner/repo",
    "description": "What it does",
    "language": "Python",
    "stars": "12.4k",
    "url": "https://github.com/...",
    "potential": "How this could be used in a marketing agency"
  }
]
```

## Execution
Use `mcp_terminal` with curl to hit the GitHub API directly.
