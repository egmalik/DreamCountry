# Competitor Intelligence Toolkit

Pulls **public data about your fitness competitors** — locations, app ratings
and reviews, financial filings, planning applications, news, price-page
history, social sentiment, and nearby events (new gyms opening on your
street, upcoming marathons in your markets) — from free/open APIs.

Full source catalog: [docs/competitor-data-apis.md](docs/competitor-data-apis.md)

## Quick start

```bash
pip install requests
cd competitor-intel
python test_connections.py   # status table: OK / FAIL / SKIPPED per source
python collect.py            # pulls everything → data/*.json + data/SUMMARY.md
```

Start by reading `data/SUMMARY.md` — it opens with the **⚠ Events & threats
feed**: competitor gyms and planning applications closest to your own clubs,
competitor-linked races, and news event signals per brand.

## Configure

Everything is driven by [`config.py`](config.py):

- `COMPETITORS` — brands to track (aliases, domains, pricing pages, App Store
  terms, SEC tickers, Companies House names)
- `OWN_CLUBS` — *your* club coordinates, used for "how close is the threat?"
- `MARKETS` — cities used for race/event searches
- `THREAT_RADIUS_KM`, `NEWS_TIMESPAN`, `EVENT_KEYWORDS` — tuning knobs

## Sources

**Tier A — free, keyless, active now:**
OpenStreetMap Overpass, Apple iTunes Search + App Store reviews RSS,
SEC EDGAR, PlanIt (UK planning applications), GDELT news, Wayback Machine
CDX, Reddit public JSON, RunSignup races.

Note: SEC EDGAR and Reddit refuse requests from datacenter IP ranges
(including GitHub Actions runners). Both work when you run `collect.py`
from an office/home network — the collectors are identical.

**Tier B — free key required (set the env var to activate):**

| Source | Env var(s) | Get a key |
|---|---|---|
| Google Places (New) | `GOOGLE_PLACES_API_KEY` | console.cloud.google.com (Places API) |
| Yelp Fusion | `YELP_API_KEY` | yelp.com/developers |
| Meta Ad Library | `META_AD_LIBRARY_TOKEN` | facebook.com/ads/library/api (identity check) |
| Companies House | `COMPANIES_HOUSE_API_KEY` | developer.company-information.service.gov.uk |
| Adzuna jobs | `ADZUNA_APP_ID` + `ADZUNA_APP_KEY` | developer.adzuna.com |
| Ticketmaster Discovery | `TICKETMASTER_API_KEY` | developer.ticketmaster.com |
| Eventbrite | `EVENTBRITE_TOKEN` | eventbrite.com/platform |

## Automation

`.github/workflows/collect.yml` re-runs the collectors on GitHub Actions
(manual **Run workflow** button, plus weekly cron once merged to the default
branch) and commits refreshed `data/` back to the branch — building a
longitudinal dataset so you can see *trends*: rating drops after a price
change, hiring surges before expansion, new sites appearing near yours.
Add the Tier B keys above as **repository secrets** to widen coverage.

## Compliance

Official/public APIs only; polite pacing and honest User-Agent throughout.
Respect each provider's terms and rate limits. Review text may contain
personal data — GDPR applies to how you store and process it.
