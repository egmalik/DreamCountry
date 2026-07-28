"""Tier B clients — fully working, activated by setting an env var each.

Each client exposes REQUIRED_ENV, probe() and fetch(); test_connections and
collect report them as SKIPPED until the key is present.
Signup links live in README.md (all have free tiers).
"""
import os

import config
from clients.http import request_json


def _env(*names):
    vals = [os.environ.get(n, "").strip() for n in names]
    return vals if all(vals) else None


# --- Google Places API (New) — ratings/reviews per competitor club ----------
class GooglePlaces:
    name = "google_places"
    REQUIRED_ENV = ["GOOGLE_PLACES_API_KEY"]
    URL = "https://places.googleapis.com/v1/places:searchText"

    def _search(self, key, text):
        import json as _json
        return request_json(
            self.URL, method="POST", data=_json.dumps({"textQuery": text}),
            headers={"X-Goog-Api-Key": key, "Content-Type": "application/json",
                     "X-Goog-FieldMask": ("places.displayName,places.rating,"
                                          "places.userRatingCount,"
                                          "places.formattedAddress")})

    def probe(self):
        (key,) = _env(*self.REQUIRED_ENV)
        data = self._search(key, "PureGym London")
        return f'{len(data.get("places", []))} place(s) returned'

    def fetch(self):
        (key,) = _env(*self.REQUIRED_ENV)
        out = {}
        for comp in config.COMPETITORS:
            for market in config.MARKETS:
                data = self._search(key, f'{comp["name"]} {market["city"]}')
                out.setdefault(comp["name"], {})[market["city"]] = \
                    data.get("places", [])[:10]
        return out


# --- Yelp Fusion — reviews/ratings ------------------------------------------
class Yelp:
    name = "yelp"
    REQUIRED_ENV = ["YELP_API_KEY"]
    URL = "https://api.yelp.com/v3/businesses/search"

    def _search(self, key, term, location):
        return request_json(self.URL,
                            params={"term": term, "location": location, "limit": 10},
                            headers={"Authorization": f"Bearer {key}"})

    def probe(self):
        (key,) = _env(*self.REQUIRED_ENV)
        data = self._search(key, "gym", "London")
        return f'{data.get("total", 0)} businesses in test search'

    def fetch(self):
        (key,) = _env(*self.REQUIRED_ENV)
        out = {}
        for comp in config.COMPETITORS:
            for market in config.MARKETS:
                data = self._search(key, comp["name"], market["city"])
                out.setdefault(comp["name"], {})[market["city"]] = [
                    {"name": b.get("name"), "rating": b.get("rating"),
                     "review_count": b.get("review_count"),
                     "address": " ".join(b.get("location", {}).get("display_address", [])),
                     "url": b.get("url")}
                    for b in data.get("businesses", [])]
        return out


# --- Meta Ad Library — competitors' live ad campaigns -----------------------
class MetaAds:
    name = "meta_ad_library"
    REQUIRED_ENV = ["META_AD_LIBRARY_TOKEN"]
    URL = "https://graph.facebook.com/v19.0/ads_archive"

    def _search(self, token, term, country):
        return request_json(self.URL, params={
            "search_terms": term, "ad_reached_countries": f'["{country}"]',
            "ad_active_status": "ACTIVE", "limit": 25,
            "fields": ("page_name,ad_delivery_start_time,ad_creative_bodies,"
                       "ad_creative_link_titles,publisher_platforms"),
            "access_token": token})

    def probe(self):
        (token,) = _env(*self.REQUIRED_ENV)
        data = self._search(token, "gym", "GB")
        return f'{len(data.get("data", []))} active ad(s) in test search'

    def fetch(self):
        (token,) = _env(*self.REQUIRED_ENV)
        out = {}
        for comp in config.COMPETITORS:
            country = "GB" if comp["country"] == "GB" else "US"
            out[comp["name"]] = self._search(token, comp["name"], country).get("data", [])
        return out


# --- Companies House (UK) — statutory accounts & filings --------------------
class CompaniesHouse:
    name = "companies_house"
    REQUIRED_ENV = ["COMPANIES_HOUSE_API_KEY"]
    BASE = "https://api.company-information.service.gov.uk"

    def _get(self, key, path, params=None):
        import base64
        auth = base64.b64encode(f"{key}:".encode()).decode()
        return request_json(self.BASE + path, params=params,
                            headers={"Authorization": f"Basic {auth}"})

    def probe(self):
        (key,) = _env(*self.REQUIRED_ENV)
        data = self._get(key, "/search/companies", {"q": "PureGym", "items_per_page": 1})
        return f'{data.get("total_results", 0)} match(es) for PureGym'

    def fetch(self):
        (key,) = _env(*self.REQUIRED_ENV)
        out = []
        for comp in config.COMPETITORS:
            query = comp.get("companies_house_query")
            if not query:
                continue
            hits = self._get(key, "/search/companies",
                             {"q": query, "items_per_page": 1}).get("items", [])
            if not hits:
                out.append({"competitor": comp["name"], "error": "no CH match"})
                continue
            num = hits[0]["company_number"]
            profile = self._get(key, f"/company/{num}")
            filings = self._get(key, f"/company/{num}/filing-history",
                                {"items_per_page": 10})
            out.append({
                "competitor": comp["name"],
                "company_number": num,
                "company_name": hits[0].get("title"),
                "status": profile.get("company_status"),
                "last_accounts": profile.get("accounts", {}).get("last_accounts"),
                "recent_filings": [
                    {"date": f.get("date"), "type": f.get("type"),
                     "description": f.get("description")}
                    for f in filings.get("items", [])],
            })
        return out


# --- Adzuna — competitor hiring (expansion signal) --------------------------
class Adzuna:
    name = "adzuna_jobs"
    REQUIRED_ENV = ["ADZUNA_APP_ID", "ADZUNA_APP_KEY"]
    URL = "https://api.adzuna.com/v1/api/jobs/gb/search/1"

    def _search(self, app_id, app_key, what):
        return request_json(self.URL, params={
            "app_id": app_id, "app_key": app_key, "what": what,
            "results_per_page": 25, "content-type": "application/json"})

    def probe(self):
        app_id, app_key = _env(*self.REQUIRED_ENV)
        data = self._search(app_id, app_key, "gym")
        return f'{data.get("count", 0)} gym job ad(s) live in GB'

    def fetch(self):
        app_id, app_key = _env(*self.REQUIRED_ENV)
        out = {}
        for comp in config.COMPETITORS:
            if comp["country"] != "GB":
                continue
            data = self._search(app_id, app_key, comp["name"])
            out[comp["name"]] = {
                "live_ads": data.get("count"),
                "sample": [{"title": j.get("title"),
                            "location": j.get("location", {}).get("display_name"),
                            "created": j.get("created")}
                           for j in data.get("results", [])[:10]],
            }
        return out


# --- Ticketmaster Discovery — ticketed sports/fitness events ----------------
class Ticketmaster:
    name = "ticketmaster_events"
    REQUIRED_ENV = ["TICKETMASTER_API_KEY"]
    URL = "https://app.ticketmaster.com/discovery/v2/events.json"

    def _search(self, key, city, keyword):
        return request_json(self.URL, params={
            "apikey": key, "city": city, "keyword": keyword,
            "classificationName": "sports", "size": 25, "sort": "date,asc"})

    def probe(self):
        (key,) = _env(*self.REQUIRED_ENV)
        data = self._search(key, "London", "run")
        return f'{data.get("page", {}).get("totalElements", 0)} event(s) in test search'

    def fetch(self):
        (key,) = _env(*self.REQUIRED_ENV)
        out = {}
        for market in config.MARKETS:
            events = []
            for kw in ("marathon", "run", "fitness"):
                data = self._search(key, market["city"], kw)
                for ev in data.get("_embedded", {}).get("events", []):
                    events.append({
                        "name": ev.get("name"),
                        "date": ev.get("dates", {}).get("start", {}).get("localDate"),
                        "url": ev.get("url"), "keyword": kw})
            out[market["city"]] = events
        return out


# --- Eventbrite — events run by known competitor organizer accounts ---------
class Eventbrite:
    name = "eventbrite"
    REQUIRED_ENV = ["EVENTBRITE_TOKEN"]
    # Public event search was retired in 2019; organizer lookup still works.
    # Add competitor organizer IDs here as you discover them on eventbrite.com.
    ORGANIZER_IDS = []
    BASE = "https://www.eventbriteapi.com/v3"

    def probe(self):
        (token,) = _env(*self.REQUIRED_ENV)
        data = request_json(f"{self.BASE}/users/me/",
                            headers={"Authorization": f"Bearer {token}"})
        return f'authenticated as {data.get("name", "unknown")}'

    def fetch(self):
        (token,) = _env(*self.REQUIRED_ENV)
        out = {}
        for org in self.ORGANIZER_IDS:
            data = request_json(
                f"{self.BASE}/organizers/{org}/events/",
                params={"status": "live"},
                headers={"Authorization": f"Bearer {token}"})
            out[org] = data.get("events", [])
        return out or {"note": "add competitor ORGANIZER_IDS in clients/keyed.py"}


TIER_B = [GooglePlaces(), Yelp(), MetaAds(), CompaniesHouse(), Adzuna(),
          Ticketmaster(), Eventbrite()]


def missing_env(client):
    return [n for n in client.REQUIRED_ENV if not os.environ.get(n, "").strip()]
