import os
import asyncio
import aiohttp
import feedparser
from datetime import datetime

FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')

RSS_FEEDS = {
    "Reuters": "http://feeds.reuters.com/reuters/businessNews",
    "Financial Times": "https://www.ft.com/?format=rss",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "Investing.com": "https://www.investing.com/rss/news_1.rss",
}

FINNHUB_URL = "https://finnhub.io/api/v1/news?category=general&token={}".format(FINNHUB_API_KEY or '')

async def fetch_json(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()

async def fetch_feed(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        text = await response.text()
        return feedparser.parse(text)

async def poll_finnhub(session, seen):
    if not FINNHUB_API_KEY:
        print("FINNHUB_API_KEY not set, skipping Finnhub news")
        return
    try:
        data = await fetch_json(session, FINNHUB_URL)
        for item in data:
            uid = item.get('id') or item.get('datetime')
            if uid in seen:
                continue
            seen.add(uid)
            ts = datetime.fromtimestamp(item['datetime']).isoformat()
            print(f"[Finnhub {ts}] {item['headline']} - {item['url']}")
    except Exception as exc:
        print(f"Error fetching Finnhub news: {exc}")

async def poll_rss(session, name, url, seen):
    try:
        feed = await fetch_feed(session, url)
        for entry in feed.entries:
            uid = entry.get('id') or entry.get('link')
            if uid in seen:
                continue
            seen.add(uid)
            ts = entry.get('published') or entry.get('updated') or ''
            print(f"[{name} {ts}] {entry.title} - {entry.link}")
    except Exception as exc:
        print(f"Error fetching {name} feed: {exc}")

async def main():
    seen = set()
    async with aiohttp.ClientSession() as session:
        while True:
            await asyncio.gather(
                poll_finnhub(session, seen),
                *[poll_rss(session, name, url, seen) for name, url in RSS_FEEDS.items()]
            )
            await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
