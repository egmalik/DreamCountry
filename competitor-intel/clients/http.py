"""Shared HTTP helper: one session, polite pacing, retries, honest User-Agent."""
import time

import requests

import config

SESSION = requests.Session()
SESSION.headers["User-Agent"] = config.CONTACT

# Seconds to sleep between calls to the same host — keeps us inside every
# free tier's politeness expectations.
PACING = 1.0
# Hosts with stricter documented limits (GDELT: max 1 request per 5s, and
# shared CI egress IPs make collisions likely — pace well below the limit).
HOST_PACING = {"api.gdeltproject.org": 8.0}

_last_call = {}


class SourceError(RuntimeError):
    """A source failed after retries; message is safe to show in reports."""


def request_json(url, params=None, method="GET", data=None, headers=None,
                 timeout=45, retries=3):
    host = url.split("/")[2]
    for attempt in range(retries):
        wait = HOST_PACING.get(host, PACING) - (time.time() - _last_call.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        try:
            resp = SESSION.request(method, url, params=params, data=data,
                                   headers=headers, timeout=timeout)
            _last_call[host] = time.time()
            if resp.status_code == 429:
                # Rate limited: wait considerably longer than normal backoff.
                time.sleep(10 * (attempt + 1))
                raise SourceError(f"HTTP 429 from {host}")
            if resp.status_code >= 500:
                raise SourceError(f"HTTP {resp.status_code} from {host}")
            if resp.status_code >= 400:
                # Client errors won't improve with retries.
                raise SourceError(
                    f"HTTP {resp.status_code} from {host}: {resp.text[:200]}")
            return resp.json()
        except SourceError as err:
            if resp.status_code < 500 and resp.status_code != 429:
                raise
            last = err
        except requests.RequestException as err:
            last = SourceError(f"{host}: {err.__class__.__name__}: {err}")
        except ValueError as err:  # non-JSON body
            raise SourceError(f"{host}: invalid JSON in response") from err
        time.sleep(2 ** attempt)
    raise last
