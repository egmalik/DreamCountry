# Public APIs for Competitor Intelligence — Fitness Industry

Catalog of public data sources for tracking competitors (PureGym, The Gym
Group, David Lloyd, Anytime Fitness, Planet Fitness, Basic-Fit, Life Time,
Xponential, …), organized by the competitive question each one answers.
✅ = implemented in this repo (`clients/`).

## 1. Locations, reviews & member sentiment

| API | What you get | Auth / cost |
|---|---|---|
| ✅ **OpenStreetMap Overpass** — `overpass-api.de/api/interpreter` | Every mapped gym/fitness centre: competitor site maps, market density, white-space analysis for new club locations | None, free |
| ✅ **Google Places API (New)** — `places.googleapis.com/v1/places:searchText` | Per-club ratings, review text, opening hours, price level; track rating trends per location | API key; ~$200/mo free credit |
| ✅ **Yelp Fusion** — `api.yelp.com/v3/businesses/search` | Reviews, ratings, categories, price tier | Free API key |
| **Foursquare Places** — `api.foursquare.com/v3/places/search` | POI details, tips, popularity signals | Free tier key |
| **Trustpilot** — `api.trustpilot.com` | Brand-level review streams for competitor chains | Key (public-data endpoints) |

## 2. Competitor mobile apps (digital product intel)

| API | What you get | Auth / cost |
|---|---|---|
| ✅ **iTunes Search** — `itunes.apple.com/search` | App ratings, rating counts, version history, release cadence | None, free |
| ✅ **App Store reviews RSS** — `itunes.apple.com/{cc}/rss/customerreviews/id={id}/json` | Latest customer reviews — where their app frustrates members | None, free |
| **google-play-scraper** (unofficial library) | Play Store ratings, reviews, installs bracket | Free; unofficial — ToS caution |

## 3. Marketing & advertising intelligence

| API | What you get | Auth / cost |
|---|---|---|
| ✅ **Meta Ad Library** — `graph.facebook.com/v19.0/ads_archive` | Every *active* Facebook/Instagram ad each competitor runs: creatives, copy, start dates, platforms — their live playbook | Free; identity-verified token |
| **TikTok Commercial Content API** | Competitor TikTok ads & branded content | Free, application required |
| **Google Ads Transparency Center** | Competitor Google ads | Web tool (no official API; SerpApi sells one) |

## 4. Social presence & content performance

| API | What you get | Auth / cost |
|---|---|---|
| ✅ **Reddit public JSON** — `reddit.com/search.json` | Unfiltered member sentiment & brand mentions | None (User-Agent required; datacenter IPs sometimes refused) |
| **YouTube Data API v3** | Competitor channel subscribers, views, upload cadence | Free key, generous quota |
| **Instagram Graph API — Business Discovery** | Follower/media counts & public-post engagement of competitor business accounts | Meta app + your own IG business account |
| **X (Twitter) API v2** | Brand mentions, share of voice | Paid tiers only |

## 5. Search demand & trends

| API | What you get | Auth / cost |
|---|---|---|
| **Google Trends** | Relative search interest: your brand vs. each competitor, by region, over time | Official API in limited alpha; `pytrends` unofficial fallback |
| **DataForSEO / SerpApi** | Competitor keyword rankings, SERP share | Paid, cheap entry |

## 6. Corporate, financial & expansion signals — the "step-ahead" tier

| API | What you get | Auth / cost |
|---|---|---|
| ✅ **SEC EDGAR** — `data.sec.gov/submissions/CIK{cik}.json` | Full filing history of US-listed rivals (Planet Fitness, Life Time, Xponential): strategy, unit economics, risk factors in 10-K/10-Q | None, free (identifying User-Agent required) |
| ✅ **Companies House (UK)** — `api.company-information.service.gov.uk` | Statutory accounts & filings of UK rivals: revenue, debt, club economics | Free API key |
| ✅ **PlanIt** — `planit.org.uk/api/applics/json` | UK planning applications — a competitor filing to open on your street shows up **months** before the doors do | None, free |
| ✅ **Adzuna** — `api.adzuna.com/v1/api/jobs/{country}/search` | Competitor job-ad volume & locations: hiring surge = expansion; roles reveal strategy | Free app id + key |
| **Greenhouse/Lever public job boards** — `boards-api.greenhouse.io`, `api.lever.co/v0/postings` | A specific rival's live vacancies, per company | None, free |
| **OpenCorporates** — `api.opencorporates.com` | Global registry data, new entity registrations | Free tier key |
| **Alpha Vantage / Financial Modeling Prep** | Stock data & earnings-call transcripts for listed rivals | Free tier keys |

## 7. Competitor events & ground-level moves

Detects things like *a rival opening a gym on the same street as one of your
clubs* or *a marathon being set up in your market*.

| Source | What you get | Auth / cost |
|---|---|---|
| ✅ **PlanIt + proximity filter** (`lat`/`lng`/`krad` params) | Gym/leisure planning applications within a radius of **your own clubs**, sorted by distance | None, free |
| ✅ **Overpass around-query** | All gyms of any brand within the threat radius of each of your clubs; re-run over time to spot new arrivals | None, free |
| ✅ **RunSignup** — `runsignup.com/rest/races` | Public race directory: upcoming marathons/5Ks by city, organizer names (spot competitor-sponsored races) | None, free |
| ✅ **GDELT 2.0 DOC** — `api.gdeltproject.org/api/v2/doc/doc` | News hits for brand + opening/launch/marathon/sponsorship/acquisition phrases | None, free |
| ✅ **Ticketmaster Discovery** — `app.ticketmaster.com/discovery/v2/events` | Ticketed sports & fitness events in your cities | Free key |
| ✅ **Eventbrite** — `eventbriteapi.com/v3/organizers/{id}/events` | Events run by known competitor organizer accounts (public search was retired in 2019) | Free token |
| ✅ **Wayback CDX** — `web.archive.org/cdx/search/cdx` | Snapshot history of competitor pricing pages → price-change timeline | None, free |

## How to stay ahead with this

1. **Run it on a schedule** (the included GitHub Actions workflow) — the edge
   comes from *deltas*: a rating drop after a price rise, a hiring surge in a
   new city, a planning application near your best club.
2. **Watch the threats feed first** (`data/SUMMARY.md`) — proximity events
   deserve same-week responses (retention offers, local marketing).
3. **Layer paid sources later** (Similarweb, Sensor Tower, BuiltWith) only
   once the free signal is being acted on.

## Compliance

- Use official APIs; respect each provider's ToS and rate limits. Avoid
  scraping where prohibited (Google Play, Google Trends, LinkedIn).
- Review text contains personal data — GDPR governs storage/processing.
- Everything here is public data: legitimate competitive intelligence.
