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


def _run(query):
    last = None
    for url in ENDPOINTS:
        try:
            return request_json(url, method="POST", data={"data": query},
                                timeout=120, retries=2)
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

    for comp in config.COMPETITORS:
        if comp["country"] != "GB":
            continue
        pattern = "|".join(re.escape(t) for t in config.brand_terms(comp))
        query = (
            '[out:json][timeout:90];'
            'area["ISO3166-1"="GB"][admin_level=2]->.uk;'
            f'nwr(area.uk)["name"~"{pattern}",i]{GYM_FILTER};'
            'out center 400;'
        )
        data = _run(query)
        out["brand_sites"][comp["name"]] = _elements_to_sites(data["elements"])

    radius_m = int(config.THREAT_RADIUS_KM * 1000)
    around = "".join(
        f'nwr(around:{radius_m},{c["lat"]},{c["lon"]}){GYM_FILTER};'
        for c in config.OWN_CLUBS)
    data = _run(f'[out:json][timeout:90];({around});out center 300;')
    out["gyms_near_our_clubs"] = _elements_to_sites(data["elements"])
    return out
