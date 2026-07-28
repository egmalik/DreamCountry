"""RunSignup Races API — public directory of upcoming races/marathons:
who is putting on endurance events in our markets, and which competitors
sponsor or organize them.

Free, keyless for public race search. Docs: https://runsignup.com/API
"""
import config
from clients.http import request_json

API = "https://runsignup.com/rest/races"


def _search(params):
    base = {"format": "json", "results_per_page": 50, "sort": "date ASC",
            "start_date": "today", "only_partner_races": "F"}
    base.update(params)
    data = request_json(API, params=base)
    races = []
    for row in data.get("races", []):
        race = row.get("race", row)
        addr = race.get("address", {})
        races.append({
            "name": race.get("name"),
            "date": race.get("next_date"),
            "city": addr.get("city"),
            "region": addr.get("state"),
            "country": addr.get("country_code"),
            "url": race.get("url"),
            "organization": race.get("club_name") or race.get("owner_name"),
        })
    return races


def probe():
    races = _search({"results_per_page": 2})
    return f'{len(races)} race(s) returned'


def fetch():
    out = {"by_market": {}, "competitor_linked": []}
    for market in config.MARKETS:
        out["by_market"][market["city"]] = _search({
            "city": market["city"], "country_code": market["country"]})
    # RunSignup is US-heavy; also scan upcoming marathons anywhere for
    # competitor names in the race or organizer fields.
    everything = _search({"name": "marathon", "results_per_page": 100})
    brands = [t.lower() for c in config.COMPETITORS for t in config.brand_terms(c)]
    for race in everything:
        hay = " ".join(str(v) for v in race.values() if v).lower()
        if any(b in hay for b in brands):
            out["competitor_linked"].append(race)
    out["upcoming_marathons_sample"] = everything[:25]
    return out
