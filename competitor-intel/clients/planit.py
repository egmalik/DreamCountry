"""PlanIt (planit.org.uk) — UK planning applications: see competitor clubs
being planned months before they open, filtered around our own sites.

Free, keyless. Docs: https://www.planit.org.uk/api/
"""
import config
from clients import geo
from clients.http import request_json

API = "https://www.planit.org.uk/api/applics/json"


def probe():
    data = request_json(API, params={"search": "gym", "pg_sz": 1})
    return f'{data.get("total", data.get("count", "?"))} matching application(s) in index'


def _simplify(rec):
    lat, lon = rec.get("lat"), rec.get("lng")
    entry = {
        "uid": rec.get("uid") or rec.get("name"),
        "authority": rec.get("area_name"),
        "date": rec.get("start_date"),
        "status": rec.get("app_state"),
        "description": (rec.get("description") or "")[:300],
        "address": rec.get("address"),
        "url": rec.get("link") or rec.get("url"),
        "lat": lat, "lon": lon,
    }
    if lat is not None and lon is not None:
        club, dist = geo.nearest_own_club(lat, lon, config.OWN_CLUBS)
        entry["nearest_own_club"] = club
        entry["distance_km"] = dist
    return entry


def _records(data):
    return data.get("records") or data.get("results") or []


def fetch():
    """Recent gym/fitness planning applications nationally, plus anything
    within THREAT_RADIUS_KM of each of our clubs (any leisure keyword)."""
    out = {"gym_applications_recent": [], "near_our_clubs": []}

    data = request_json(API, params={
        "search": "gym OR fitness", "recent": 120, "pg_sz": 100})
    out["gym_applications_recent"] = [_simplify(r) for r in _records(data)]

    seen = set()
    for club in config.OWN_CLUBS:
        data = request_json(API, params={
            "search": "gym OR fitness OR leisure",
            "lat": club["lat"], "lng": club["lon"],
            "krad": config.THREAT_RADIUS_KM, "recent": 365, "pg_sz": 50})
        for rec in _records(data):
            entry = _simplify(rec)
            if entry["uid"] in seen:
                continue
            seen.add(entry["uid"])
            out["near_our_clubs"].append(entry)
    out["near_our_clubs"].sort(key=lambda e: e.get("distance_km", 999))
    return out
