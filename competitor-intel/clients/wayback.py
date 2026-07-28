"""Internet Archive Wayback CDX API — snapshot history of competitor pricing
pages, so price/offer changes can be diffed over time.

Free, keyless. Docs: https://archive.org/developers/wayback-cdx-server.html
"""
import config
from clients.http import request_json, SourceError

CDX = "https://web.archive.org/cdx/search/cdx"


def probe():
    rows = request_json(CDX, params={"url": "puregym.com", "output": "json",
                                     "limit": 2})
    return f'{max(len(rows) - 1, 0)} snapshot row(s) returned'


def fetch():
    out = {}
    for comp in config.COMPETITORS:
        pages = []
        for url in comp.get("pricing_urls", []):
            try:
                rows = request_json(CDX, params={
                    "url": url, "output": "json", "collapse": "digest",
                    "fl": "timestamp,original,statuscode", "limit": -30},
                    timeout=60, retries=2)
            except SourceError as err:
                pages.append({"url": url, "error": str(err)})
                continue
            snaps = [{
                "timestamp": r[0],
                "replay_url": f"https://web.archive.org/web/{r[0]}/{r[1]}",
                "status": r[2],
            } for r in rows[1:]]  # row 0 is the header
            pages.append({"url": url,
                          "distinct_versions_recent": len(snaps),
                          "snapshots": snaps})
        out[comp["name"]] = pages
    return out
