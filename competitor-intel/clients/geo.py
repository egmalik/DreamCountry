"""Small geo helpers shared by proximity-aware collectors."""
import math


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def nearest_own_club(lat, lon, own_clubs):
    """Return (club_name, distance_km) of the closest of our clubs."""
    best = min(own_clubs, key=lambda c: haversine_km(lat, lon, c["lat"], c["lon"]))
    return best["name"], round(haversine_km(lat, lon, best["lat"], best["lon"]), 2)
