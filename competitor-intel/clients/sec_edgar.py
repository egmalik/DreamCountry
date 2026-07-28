"""SEC EDGAR — filings of US-listed competitors (10-K/10-Q/8-K).

Free, keyless; requires an identifying User-Agent (set globally in http.py).
Docs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
"""
import config
from clients.http import request_json

TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
INTERESTING_FORMS = {"10-K", "10-Q", "8-K", "S-1", "DEF 14A"}


def _cik_map():
    data = request_json(TICKERS_URL)
    return {row["ticker"].upper(): row["cik_str"] for row in data.values()}


def probe():
    ciks = _cik_map()
    return f'ticker map loaded ({len(ciks)} companies); PLNT CIK={ciks.get("PLNT")}'


def fetch():
    ciks = _cik_map()
    out = []
    for comp in config.COMPETITORS:
        ticker = comp.get("sec_ticker")
        if not ticker:
            continue
        cik = ciks.get(ticker.upper())
        if cik is None:
            out.append({"competitor": comp["name"], "ticker": ticker,
                        "error": "ticker not found in EDGAR"})
            continue
        sub = request_json(SUBMISSIONS.format(cik=cik))
        recent = sub.get("filings", {}).get("recent", {})
        filings = []
        for form, date, accession, doc in zip(recent.get("form", []),
                                              recent.get("filingDate", []),
                                              recent.get("accessionNumber", []),
                                              recent.get("primaryDocument", [])):
            if form in INTERESTING_FORMS:
                acc = accession.replace("-", "")
                filings.append({
                    "form": form, "date": date,
                    "url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{doc}",
                })
            if len(filings) >= 8:
                break
        out.append({
            "competitor": comp["name"], "ticker": ticker, "cik": cik,
            "company_name": sub.get("name"),
            "sic_description": sub.get("sicDescription"),
            "recent_filings": filings,
        })
    return out
