#!/usr/bin/env python3
"""Hit every source with the cheapest possible call and print a status table.

Exit code 0 if all keyless (Tier A) sources are OK, 1 otherwise.
Tier B sources without keys are SKIPPED and never fail the run.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from clients import appstore, gdelt, overpass, planit, reddit, runsignup, sec_edgar, wayback
from clients import keyed

TIER_A = [
    ("overpass_osm", overpass),
    ("apple_appstore", appstore),
    ("sec_edgar", sec_edgar),
    ("planit_uk", planit),
    ("gdelt_news", gdelt),
    ("wayback_machine", wayback),
    ("reddit", reddit),
    ("runsignup_races", runsignup),
]

# Sources where cloud-runner IPs are known to be refused sometimes; a failure
# is reported but doesn't fail the suite.
BEST_EFFORT = {"reddit"}


def main():
    rows, hard_fail = [], False
    for name, mod in TIER_A:
        try:
            rows.append((name, "OK", mod.probe()))
        except Exception as err:  # noqa: BLE001 - report every failure mode
            status = "WARN" if name in BEST_EFFORT else "FAIL"
            hard_fail |= status == "FAIL"
            rows.append((name, status, str(err)[:140]))

    for client in keyed.TIER_B:
        missing = keyed.missing_env(client)
        if missing:
            rows.append((client.name, "SKIPPED", f'set {" + ".join(missing)}'))
            continue
        try:
            rows.append((client.name, "OK", client.probe()))
        except Exception as err:  # noqa: BLE001
            hard_fail = True
            rows.append((client.name, "FAIL", str(err)[:140]))

    width = max(len(r[0]) for r in rows)
    print(f'{"SOURCE".ljust(width)}  {"STATUS":8}DETAIL')
    for name, status, detail in rows:
        print(f"{name.ljust(width)}  {status:8}{detail}")

    print()
    if hard_fail:
        print("RESULT: some required sources FAILED")
        return 1
    print("RESULT: all reachable sources OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
