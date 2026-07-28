"""Reddit public JSON search — unfiltered member sentiment about competitors.

Keyless read of public listings (a descriptive User-Agent is required).
Cloud-runner IPs are sometimes blocked with 403 — reported, not fatal.
"""
import config
from clients.http import request_json, SourceError

SEARCH = "https://www.reddit.com/search.json"


def probe():
    data = request_json(SEARCH, params={"q": '"puregym"', "limit": 2, "t": "month"})
    return f'{len(data.get("data", {}).get("children", []))} post(s) returned'


def fetch():
    out = {}
    for comp in config.COMPETITORS:
        try:
            data = request_json(SEARCH, params={
                "q": f'"{comp["name"]}"', "sort": "new", "limit": 15, "t": "month"})
            out[comp["name"]] = [{
                "title": c["data"].get("title"),
                "subreddit": c["data"].get("subreddit"),
                "score": c["data"].get("score"),
                "num_comments": c["data"].get("num_comments"),
                "created_utc": c["data"].get("created_utc"),
                "url": "https://www.reddit.com" + c["data"].get("permalink", ""),
            } for c in data.get("data", {}).get("children", [])]
        except SourceError as err:
            out[comp["name"]] = [{"error": str(err)}]
    return out
