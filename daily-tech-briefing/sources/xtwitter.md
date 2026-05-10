---
name: source-xtwitter
description: Monitor X/Twitter for trending AI topics and posts from key influencers
category: research
---

# Source: X/Twitter

Monitor trending AI topics and key influencer posts on X.

## Target Accounts
```
balajis, naval, paulg, sama, karpathy, gdb, garrytan, mwseibel, daltonc
levelsio, rauchg, StevenBartlett, ChrisWillx, tbpn
```

## Trending Topics to Check
- AI agents
- GPT-5 / LLMs
- AI startups
- Marketing automation
- Indie hacking
- Bootstrapping

## Method
Use browser_navigate to:
1. Check X trending topics: `https://x.com/i/flow/trends`
2. Check influencer timelines/posts

## Data to Extract
- Trending topics/hashtags
- Notable posts from influencers
- Any viral AI news
- Threads about AI tools or business

## Filtering
- Prioritize posts about AI tools, products, implementations
- Business and entrepreneurship opportunities
- Marketing applications of AI
- Anything that could apply to a marketing agency

## Output Format
```json
{
  "trending_topics": ["#AITools", "#AIAgents", etc],
  "top_posts": [
    {
      "author": "@handle",
      "name": "Real Name",
      "content": "Post text excerpt...",
      "url": "https://x.com/...",
      "relevance": "Why this matters"
    }
  ]
}
```

## Execution
Use browser_navigate + browser_snapshot to check X. Use web_search for trending topics.
