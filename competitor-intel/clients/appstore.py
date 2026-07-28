"""Apple iTunes Search API + App Store RSS — competitor app ratings & reviews.

Free, keyless. Search docs:
https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/
"""
import config
from clients.http import request_json, SourceError

SEARCH = "https://itunes.apple.com/search"
REVIEWS = "https://itunes.apple.com/{cc}/rss/customerreviews/id={app_id}/sortby=mostrecent/json"


def probe():
    data = request_json(SEARCH, params={"term": "PureGym", "entity": "software",
                                        "country": "gb", "limit": 1})
    return f'{data.get("resultCount", 0)} app(s) found'


def _best_match(results, term):
    term_l = term.lower()
    for r in results:
        if term_l in r.get("trackName", "").lower():
            return r
    return results[0] if results else None


def fetch():
    apps = []
    for comp in config.COMPETITORS:
        cfg = comp["appstore"]
        try:
            data = request_json(SEARCH, params={
                "term": cfg["term"], "entity": "software",
                "country": cfg["country"], "limit": 5})
        except SourceError as err:
            apps.append({"competitor": comp["name"], "error": str(err)})
            continue
        app = _best_match(data.get("results", []), cfg["term"])
        if not app:
            apps.append({"competitor": comp["name"], "error": "no app found"})
            continue
        entry = {
            "competitor": comp["name"],
            "app_name": app.get("trackName"),
            "app_id": app.get("trackId"),
            "rating": app.get("averageUserRating"),
            "rating_count": app.get("userRatingCount"),
            "current_version": app.get("version"),
            "last_updated": app.get("currentVersionReleaseDate"),
            "genre": app.get("primaryGenreName"),
            "recent_reviews": [],
        }
        try:
            rss = request_json(REVIEWS.format(cc=cfg["country"], app_id=app["trackId"]))
            for item in rss.get("feed", {}).get("entry", [])[:5]:
                entry["recent_reviews"].append({
                    "title": item.get("title", {}).get("label"),
                    "rating": item.get("im:rating", {}).get("label"),
                    "text": item.get("content", {}).get("label", "")[:400],
                    "version": item.get("im:version", {}).get("label"),
                })
        except SourceError as err:
            entry["reviews_error"] = str(err)
        apps.append(entry)
    return apps
