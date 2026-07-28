"""OpenStreetMap Overpass API — competitor gym locations + gyms near our clubs.

Free, keyless. Docs: https://wiki.openstreetmap.org/wiki/Overpass_API
Mirrors are tried in order because the main instance rate-limits.
"""
import re

import config
from clients import geo
from clients.http import request_json, SourceError

ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.osm.jp/api/interpreter",
]

GYM_FILTER = '["leisure"~"fitness_centre|sports_centre|gym"]'
# Great Britain bounding box — mirrors without area data silently return
# empty results for area queries, so a bbox is far more reliable.
UK_BBOX = "(49.8,-8.7,60.9,1.8)"


def _run(query, expect_results=False):
    last = None
    for url in ENDPOINTS:
        try:
            data = request_json(url, method="POST", data={"data": query},
                                timeout=180, retries=2)
            if expect_results and not data.get("elements"):
                # A mirror missing data answers 200 with nothing — that is a
                # failure for queries that must match (major chains exist).
                last = SourceError(f"{url.split('/')[2]}: empty result")
                continue
            return data
        except SourceError as err:
            last = err
    raise last


def _elements_to_sites(elements):
    sites = []
    for el in elements:
        lat = el.get("lat") or el.get("center", {}).get("lat")
        lon = el.get("lon") or el.get("center", {}).get("lon")
        if lat is None:
            continue
        tags = el.get("tags", {})
        club, dist = geo.nearest_own_club(lat, lon, config.OWN_CLUBS)
        sites.append({
            "osm_id": f'{el["type"]}/{el["id"]}',
            "name": tags.get("name"),
            "brand": tags.get("brand"),
            "lat": lat, "lon": lon,
            "address": " ".join(filter(None, [tags.get("addr:housenumber"),
                                              tags.get("addr:street"),
                                              tags.get("addr:city"),
                                              tags.get("addr:postcode")])) or None,
            "nearest_own_club": club,
            "distance_km": dist,
        })
    sites.sort(key=lambda s: s["distance_km"])
    return sites


def probe():
    data = _run('[out:json][timeout:20];node["leisure"="fitness_centre"]'
                '(51.50,-0.15,51.52,-0.12);out 1;')
    return f'{len(data.get("elements", []))} element(s) returned'


def fetch():
    """Two views: every UK site per competitor brand, and all gyms of any
    brand within THREAT_RADIUS_KM of our own clubs."""
    out = {"brand_sites": {}, "gyms_near_our_clubs": []}

    # One combined query for every tracked brand — sequential per-brand
    # queries trip Overpass rate limits and take 6x as long.
    gb_comps = [c for c in config.COMPETITORS if c["country"] == "GB"]
    pattern = "|".join(re.escape(t) for c in gb_comps
                       for t in config.brand_terms(c))
    query = (
        '[out:json][timeout:150];'
        f'nwr{UK_BBOX}["name"~"{pattern}",i]{GYM_FILTER};'
        'out center 2000;'
    )
    sites = _elements_to_sites(_run(query, expect_results=True)["elements"])
    for comp in gb_comps:
        terms = [t.lower() for t in config.brand_terms(comp)]
        out["brand_sites"][comp["name"]] = [
            s for s in sites
            if any(t in (s["name"] or s["brand"] or "").lower() for t in terms)]

    radius_m = int(config.THREAT_RADIUS_KM * 1000)
    around = "".join(
        f'nwr(around:{radius_m},{c["lat"]},{c["lon"]}){GYM_FILTER};'
        for c in config.OWN_CLUBS)
    data = _run(f'[out:json][timeout:90];({around});out center 300;')
    out["gyms_near_our_clubs"] = _elements_to_sites(data["elements"])
    return out
