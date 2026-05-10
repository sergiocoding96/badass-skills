---
name: source-youtube
description: Check latest YouTube videos from key AI/entrepreneurship channels
category: research
---

# Source: YouTube Videos

Check the latest uploads from key AI and entrepreneurship YouTube channels.

## Target Channels
```
Simon Høiberg
Starter Story
Nathan Latka
Liam Ottley
Matt Diggity
Two Minute Papers
AI Explained
Fahim LA
Y Combinator
SaaStr
Brian Casel
IndyDevDan
All About AI
Builders Central
Alex Finn
Greg Isenberg
Craig Hewitt
Nick Saraev
AI Engineer
Nate Herk
Grace Leung
Ben AI
```

## Method
Use `youtube-content` skill or browser-based approach:
1. Search for latest videos from each channel
2. Extract: video title, channel, published date, description
3. Focus on videos from last 48-72 hours

## Alternative: YouTube Data API approach
```
GET https://www.googleapis.com/youtube/v3/search
  ?key=API_KEY
  &channelId=CHANNEL_ID
  &part=snippet
  &order=date
  &maxResults=5
```

## Filtering Criteria
- AI tools and implementations
- Business case studies
- Marketing automation
- Building and scaling products
- Founder interviews and stories
- Anything relevant to a marketing agency

## Output Format
```json
[
  {
    "title": "Video Title",
    "channel": "Channel Name",
    "url": "https://youtube.com/watch?v=...",
    "published": "2026-04-03",
    "summary": "What the video covers",
    "relevance": "Why this matters for a marketing agency"
  }
]
```

## Execution
Use browser_navigate + browser_snapshot to check channel pages, or use web_search to find latest videos.
