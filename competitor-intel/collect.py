#!/usr/bin/env python3
"""Run every available collector and write results + a human summary to data/.

Each source writes data/<source>.json:
    {"source": ..., "collected_at": ..., "ok": bool, "data" | "error": ...}
A failing source never aborts the run. Exit code 1 only if every keyless
source failed (nothing at all was collected).
"""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from clients import appstore, gdelt, overpass, planit, reddit, runsignup, sec_edgar, wayback
from clients import keyed

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

TIER_A = [
    ("overpass_osm", overpass.fetch),
    ("apple_appstore", appstore.fetch),
    ("sec_edgar", sec_edgar.fetch),
    ("planit_uk", planit.fetch),
    ("gdelt_news", gdelt.fetch),
    ("wayback_machine", wayback.fetch),
    ("reddit", reddit.fetch),
    ("runsignup_races", runsignup.fetch),
]


def run_source(name, fn):
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    print(f"[collect] {name} ...", flush=True)
    try:
        payload = {"source": name, "collected_at": stamp, "ok": True, "data": fn()}
    except Exception as err:  # noqa: BLE001 - a source must never kill the run
        print(f"[collect] {name} FAILED: {err}", flush=True)
        payload = {"source": name, "collected_at": stamp, "ok": False,
                   "error": str(err)[:300]}
    path = os.path.join(DATA_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False)
    print(f"[collect] {name} -> {os.path.basename(path)} ok={payload['ok']}",
          flush=True)
    return payload


def summarize(results):
    """data/SUMMARY.md — headline numbers + the events & threats feed."""
    get = lambda n: results.get(n, {}).get("data") if results.get(n, {}).get("ok") else None
    lines = ["# Competitor Intelligence — Snapshot",
             f"\n_Collected {results[next(iter(results))]['collected_at']} — sources: "
             f"{sum(r['ok'] for r in results.values())}/{len(results)} OK_\n"]

    lines.append("## ⚠ Events & threats feed\n")
    threats = []
    osm = get("overpass_osm")
    if osm:
        for gym in osm["gyms_near_our_clubs"][:10]:
            threats.append(f"- **Gym {gym['distance_km']} km from {gym['nearest_own_club']}**: "
                           f"{gym['name'] or gym['brand'] or 'unnamed'} ({gym.get('address') or 'no address'})")
    plan = get("planit_uk")
    if plan:
        for app in plan["near_our_clubs"][:10]:
            if app.get("distance_km") is not None:
                where = f"{app['distance_km']} km from {app['nearest_own_club']}"
            else:
                where = (f"within {config.THREAT_RADIUS_KM} km of "
                         f"{app.get('nearest_own_club', 'a club')}")
            threats.append(f"- **Planning application {where}** [{app.get('status')}]: "
                           f"{app.get('description') or ''} — {app.get('address') or ''}")
    races = get("runsignup_races")
    if races:
        for race in races.get("competitor_linked", [])[:5]:
            threats.append(f"- **Competitor-linked race**: {race['name']} on {race['date']} "
                           f"({race.get('city')}, {race.get('country')})")
        for city, items in races.get("by_market", {}).items():
            for race in items[:3]:
                threats.append(f"- **Upcoming race in {city}**: {race['name']} on {race['date']}")
    news = get("gdelt_news")
    if news:
        for brand, arts in news["event_signals"].items():
            for a in arts[:2]:
                if a.get("title"):
                    threats.append(f"- **{brand} event signal**: [{a['title']}]({a['url']}) "
                                   f"({a.get('source')}, {a.get('date')})")
    lines.extend(threats or ["_No threat signals collected this run._"])

    lines.append("\n## Competitor estate (OpenStreetMap)\n")
    if osm:
        lines.append("| Competitor | Mapped UK sites | Closest to one of our clubs |")
        lines.append("|---|---|---|")
        for brand, sites in osm["brand_sites"].items():
            closest = (f"{sites[0]['distance_km']} km ({sites[0]['nearest_own_club']})"
                       if sites else "—")
            lines.append(f"| {brand} | {len(sites)} | {closest} |")
    else:
        lines.append("_source failed this run_")

    lines.append("\n## Competitor apps (Apple App Store)\n")
    apps = get("apple_appstore")
    if apps:
        lines.append("| Competitor | App | Rating | Ratings count | Last update |")
        lines.append("|---|---|---|---|---|")
        for a in apps:
            if a.get("error"):
                lines.append(f"| {a['competitor']} | _{a['error']}_ | | | |")
            else:
                lines.append(f"| {a['competitor']} | {a['app_name']} | {a['rating']} "
                             f"| {a['rating_count']} | {a['last_updated']} |")
    else:
        lines.append("_source failed this run_")

    lines.append("\n## Latest SEC filings (US-listed rivals)\n")
    sec = get("sec_edgar")
    if sec:
        for entry in sec:
            if entry.get("error"):
                lines.append(f"- {entry['competitor']}: _{entry['error']}_")
                continue
            latest = entry["recent_filings"][:3]
            fil = "; ".join(f"[{f['form']} {f['date']}]({f['url']})" for f in latest)
            lines.append(f"- **{entry['competitor']}** ({entry['ticker']}): {fil}")
    else:
        lines.append("_source failed this run_")

    lines.append("\n## Pricing-page change history (Wayback)\n")
    wb = get("wayback_machine")
    if wb:
        for brand, pages in wb.items():
            for page in pages:
                if page.get("error"):
                    continue
                lines.append(f"- **{brand}**: {page['distinct_versions_recent']} distinct "
                             f"recent versions of `{page['url']}`")
    lines.append("\n## Source status\n")
    for name, res in results.items():
        lines.append(f"- `{name}`: {'OK' if res['ok'] else 'FAILED — ' + res['error']}")

    with open(os.path.join(DATA_DIR, "SUMMARY.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"[collect] wrote SUMMARY.md ({len(threats)} threat signals)")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    results = {name: run_source(name, fn) for name, fn in TIER_A}
    for client in keyed.TIER_B:
        if keyed.missing_env(client):
            print(f"[collect] {client.name} skipped (set "
                  f"{' + '.join(keyed.missing_env(client))})")
            continue
        results[client.name] = run_source(client.name, client.fetch)

    summarize(results)
    if not any(r["ok"] for r in results.values()):
        print("RESULT: every source failed")
        return 1
    print(f"RESULT: {sum(r['ok'] for r in results.values())}/{len(results)} sources collected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
