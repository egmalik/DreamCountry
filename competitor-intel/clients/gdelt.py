"""GDELT 2.0 DOC API — global news monitoring: brand mentions + event signals
(openings, marathons, sponsorships, acquisitions).

Free, keyless. Docs: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
"""
import config
from clients.http import request_json, SourceError

API = "https://api.gdeltproject.org/api/v2/doc/doc"


def _search(query, maxrecords=25):
    data = request_json(API, params={
        "query": query,
        "mode": "artlist", "format": "json",
        "maxrecords": maxrecords, "timespan": config.NEWS_TIMESPAN,
        "sort": "datedesc"}, retries=2)
    return [{
        "title": a.get("title"),
        "url": a.get("url"),
        "date": a.get("seendate"),
        "source": a.get("domain"),
        "country": a.get("sourcecountry"),
    } for a in data.get("articles", [])]


def probe():
    arts = _search('"PureGym"', maxrecords=2)
    return f'{len(arts)} article(s) returned'


def fetch():
    out = {"brand_news": {}, "event_signals": {}}
    for comp in config.COMPETITORS:
        name = comp["name"]
        quoted = comp.get("news_query") or f'"{name}"'
        try:
            out["brand_news"][name] = _search(quoted, maxrecords=15)
        except SourceError as err:
            out["brand_news"][name] = [{"error": str(err)}]
        try:
            out["event_signals"][name] = _search(
                f"{quoted} {config.EVENT_KEYWORDS}", maxrecords=15)
        except SourceError as err:
            out["event_signals"][name] = [{"error": str(err)}]
    return out
