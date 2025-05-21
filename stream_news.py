import os
import time
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')

RSS_FEEDS = {
    "Reuters": "http://feeds.reuters.com/reuters/businessNews",
    "Financial Times": "https://www.ft.com/?format=rss",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "Investing.com": "https://www.investing.com/rss/news_1.rss",
}

FINNHUB_URL = "https://finnhub.io/api/v1/news?category=general&token={}".format(
    FINNHUB_API_KEY or ""
)


def fetch_url(url):
    with urllib.request.urlopen(url) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset)


def fetch_feed(url):
    text = fetch_url(url)
    root = ET.fromstring(text)
    entries = []
    for item in root.findall(".//item"):
        entry = {
            "id": item.findtext("guid") or item.findtext("link"),
            "title": item.findtext("title"),
            "link": item.findtext("link"),
            "published": item.findtext("pubDate"),
        }
        entries.append(entry)
    return entries


def poll_finnhub(seen):
    if not FINNHUB_API_KEY:
        print("FINNHUB_API_KEY not set, skipping Finnhub news")
        return
    try:
        text = fetch_url(FINNHUB_URL)
        data = json.loads(text)
        for item in data:
            uid = str(item.get("id") or item.get("datetime"))
            if uid in seen:
                continue
            seen.add(uid)
            ts = item.get("datetime")
            if isinstance(ts, (int, float)):
                ts = datetime.fromtimestamp(ts).isoformat()
            print(f"[Finnhub {ts}] {item.get('headline')} - {item.get('url')}")
    except Exception as exc:
        print(f"Error fetching Finnhub news: {exc}")


def poll_rss(name, url, seen):
    try:
        feed = fetch_feed(url)
        for entry in feed:
            uid = entry["id"]
            if uid in seen:
                continue
            seen.add(uid)
            ts = entry.get("published") or ""
            print(f"[{name} {ts}] {entry['title']} - {entry['link']}")
    except Exception as exc:
        print(f"Error fetching {name} feed: {exc}")


def main():
    seen = set()
    while True:
        poll_finnhub(seen)
        for name, url in RSS_FEEDS.items():
            poll_rss(name, url, seen)
        time.sleep(60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
