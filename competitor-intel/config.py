"""Central registry: who we track, where our own clubs are, and tuning knobs.

Edit this file to add/remove competitors or your own club locations —
every collector reads from here.
"""

# Contact string sent in User-Agent headers. SEC EDGAR and Overpass ask for
# an identifiable contact; keep this accurate.
CONTACT = "FitnessFirst CompetitorIntel (github.com/egmalik/dreamcountry)"

# Radius (km) around our own clubs used for "threat" proximity checks
# (new competitor sites, planning applications, nearby gyms).
THREAT_RADIUS_KM = 3.0

# How far back news / social searches look.
NEWS_TIMESPAN = "3months"

COMPETITORS = [
    {
        "name": "PureGym",
        "aliases": ["Pure Gym"],
        "country": "GB",
        "domain": "puregym.com",
        "pricing_urls": ["https://www.puregym.com/join/"],
        "appstore": {"term": "PureGym", "country": "gb"},
        "sec_ticker": None,
        "companies_house_query": "PureGym Limited",
    },
    {
        "name": "The Gym Group",
        "aliases": ["TheGym", "The Gym"],
        "country": "GB",
        "domain": "thegymgroup.com",
        "pricing_urls": ["https://www.thegymgroup.com/join-now/"],
        "appstore": {"term": "The Gym Group", "country": "gb"},
        "sec_ticker": None,
        "companies_house_query": "The Gym Group plc",
    },
    {
        "name": "David Lloyd",
        "aliases": ["David Lloyd Leisure", "David Lloyd Clubs"],
        "country": "GB",
        "domain": "davidlloyd.co.uk",
        "pricing_urls": ["https://www.davidlloyd.co.uk/memberships/"],
        "appstore": {"term": "David Lloyd Clubs", "country": "gb"},
        "sec_ticker": None,
        "companies_house_query": "David Lloyd Leisure Limited",
    },
    {
        "name": "Anytime Fitness",
        "aliases": [],
        "country": "GB",
        "domain": "anytimefitness.co.uk",
        "pricing_urls": ["https://www.anytimefitness.co.uk/membership/"],
        "appstore": {"term": "Anytime Fitness", "country": "gb"},
        "sec_ticker": None,
        "companies_house_query": "Anytime Fitness UK",
    },
    {
        "name": "Nuffield Health",
        "aliases": [],
        "country": "GB",
        "domain": "nuffieldhealth.com",
        "pricing_urls": ["https://www.nuffieldhealth.com/gyms"],
        "appstore": {"term": "Nuffield Health", "country": "gb"},
        "sec_ticker": None,
        "companies_house_query": "Nuffield Health",
    },
    {
        "name": "Virgin Active",
        "aliases": [],
        "country": "GB",
        "domain": "virginactive.co.uk",
        "pricing_urls": ["https://www.virginactive.co.uk/memberships"],
        "appstore": {"term": "Virgin Active", "country": "gb"},
        "sec_ticker": None,
        "companies_house_query": "Virgin Active Limited",
    },
    {
        "name": "Basic-Fit",
        "aliases": ["BasicFit"],
        "country": "NL",
        "domain": "basic-fit.com",
        "pricing_urls": ["https://www.basic-fit.com/en-gb/memberships"],
        "appstore": {"term": "Basic-Fit", "country": "gb"},
        "sec_ticker": None,  # Euronext-listed; annual reports on basic-fit.com IR pages
        "companies_house_query": None,
    },
    {
        "name": "Planet Fitness",
        "aliases": [],
        "country": "US",
        "domain": "planetfitness.com",
        "pricing_urls": ["https://www.planetfitness.com/gym-memberships"],
        "appstore": {"term": "Planet Fitness", "country": "us"},
        "sec_ticker": "PLNT",
        "companies_house_query": None,
    },
    {
        "name": "Life Time",
        # "Life Time" alone matches the everyday phrase in news text.
        "news_query": '"Life Time" (gym OR fitness OR "health club")',
        "aliases": ["Life Time Fitness"],
        "country": "US",
        "domain": "lifetime.life",
        "pricing_urls": ["https://www.lifetime.life/membership.html"],
        "appstore": {"term": "Life Time", "country": "us"},
        "sec_ticker": "LTH",
        "companies_house_query": None,
    },
    {
        "name": "Xponential Fitness",
        "aliases": ["Club Pilates", "Pure Barre", "CycleBar"],
        "country": "US",
        "domain": "xponential.com",
        "pricing_urls": ["https://www.xponential.com/"],
        "appstore": {"term": "Club Pilates", "country": "us"},
        "sec_ticker": "XPOF",
        "companies_house_query": None,
    },
]

# Your own club locations (sample set — replace with the full estate).
# Used to answer "is a competitor moving in on my street?".
OWN_CLUBS = [
    {"name": "Fitness First Tottenham Court Road", "lat": 51.5174, "lon": -0.1303},
    {"name": "Fitness First Liverpool Street", "lat": 51.5179, "lon": -0.0823},
    {"name": "Fitness First Baker Street", "lat": 51.5203, "lon": -0.1567},
    {"name": "Fitness First Hammersmith", "lat": 51.4927, "lon": -0.2243},
    {"name": "Fitness First Clapham Junction", "lat": 51.4645, "lon": -0.1700},
]

# Markets (cities) used for event searches (races, marathons, ticketed events).
MARKETS = [
    {"city": "London", "country": "GB", "lat": 51.5074, "lon": -0.1278},
    {"city": "Manchester", "country": "GB", "lat": 53.4808, "lon": -2.2426},
]

# Phrases that turn a plain news search into an "event / move" search.
EVENT_KEYWORDS = (
    '(opening OR "new gym" OR "new club" OR launch OR expansion OR '
    'marathon OR "fun run" OR sponsorship OR partnership OR acquisition)'
)

def brand_terms(comp):
    """All name variants for a competitor, longest first."""
    return sorted([comp["name"], *comp.get("aliases", [])], key=len, reverse=True)
