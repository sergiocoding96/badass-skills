---
name: source-blogs
description: Scrape top tech/AI blogs and news sites for daily briefing
category: research
---

# Source: Tech/AI Blog Posts

Scrape the following sources for the latest AI and tech news:

## Target Sources
- Hacker News (top stories tagged AI/tech)
- VentureBeat AI
- TechCrunch (AI section)
- The Verge (AI section)
- MIT Technology Review
- Ars Technica (AI section)
- AI News (ainews.ai)
- Import AI newsletter format

## Firecrawl Config
- Use Firecrawl on `http://localhost:3002`
- Endpoint: `POST /api/scrape`
- Extract: title, summary, url, published_date
- Limit: 15-20 articles total

## Filtering Criteria
- AI/ML tools and products
- Autonomous agents
- Business applications of AI
- Marketing automation with AI
- Startup funding in AI space
- New AI platforms or services

## Output Format
Return a JSON array:
```json
[
  {
    "source": "HN/VentureBeat/etc",
    "title": "Article Title",
    "url": "https://...",
    "summary": "2-3 sentence summary",
    "relevance": "why this matters for a marketing agency owner"
  }
]
```

## Execution
Use web_search + web_extract to gather content. Prioritize recency (last 24-48 hours).
