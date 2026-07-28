"""GDELT 2.0 DOC API — global news monitoring: brand mentions + event signals
(openings, marathons, sponsorships, acquisitions).

Free, keyless. Docs: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
"""
import re

import config
from clients.http import request_json, SourceError

API = "https://api.gdeltproject.org/api/v2/doc/doc"

EVENT_TERMS = re.compile(
    r"\b(open(s|ing|ed)?|new (gym|club|location|site)|launch|expan(d|sion)|"
    r"marathon|fun run|sponsor|partnership|acqui(re|sition)|invest)\b",
    re.IGNORECASE)


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
    """One query per brand; event signals are filtered client-side from the
    same articles (halves API calls — GDELT rate-limits aggressively)."""
    out = {"brand_news": {}, "event_signals": {}}
    for comp in config.COMPETITORS:
        name = comp["name"]
        quoted = comp.get("news_query") or f'"{name}"'
        try:
            articles = _search(quoted, maxrecords=40)
        except SourceError as err:
            out["brand_news"][name] = [{"error": str(err)}]
            out["event_signals"][name] = []
            continue
        out["brand_news"][name] = articles[:15]
        out["event_signals"][name] = [
            a for a in articles if EVENT_TERMS.search(a.get("title") or "")]
    return out
