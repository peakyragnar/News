# Streaming News Agent

This repository contains a simple Python script that streams headlines from several free news feeds:

- Reuters RSS
- Financial Times RSS
- Yahoo Finance RSS
- Investing.com RSS
- Finnhub API

The script polls each source periodically and prints any new headlines to the console.

## Requirements

- Python 3.8+
- `aiohttp` and `feedparser` libraries (`pip install aiohttp feedparser`)
- A Finnhub API key exported as `FINNHUB_API_KEY` in your environment if you want to include Finnhub news.

## Usage

```bash
export FINNHUB_API_KEY=your_key_here  # optional
python stream_news.py
```

The script runs continuously, polling for new headlines every minute. Press `Ctrl+C` to stop it.
