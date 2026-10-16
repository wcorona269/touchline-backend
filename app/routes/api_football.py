import json
import os
import http.client
import threading
from dotenv import load_dotenv
from ..extensions import cache
from .seasons import current_season
load_dotenv(".flaskenv")

HOST = "v3.football.api-sports.io"
HEADERS = {
    'x-rapidapi-host': HOST,
    'x-rapidapi-key': os.getenv("API_KEY"),
}


class ApiFootballError(Exception):
    """api-sports reports failures (e.g. the free plan's 10 requests/minute limit) in an `errors`
    field with HTTP 200 and an empty `response`, which is indistinguishable from "no data"
    unless checked explicitly."""


def api_get(path, conn=None):
    conn = conn or http.client.HTTPSConnection(HOST)
    conn.request("GET", path, headers=HEADERS)
    body = json.loads(conn.getresponse().read().decode("utf-8"))
    if body.get('errors'):
        raise ApiFootballError(body['errors'])
    return body['response']


def is_success(rv):
    """Flask-Caching response_filter: never cache an error response, so a rate-limited
    request doesn't pin an empty page for the whole cache timeout."""
    return not (isinstance(rv, tuple) and len(rv) > 1 and rv[1] != 200)


MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY

_inflight_locks = {}
_inflight_guard = threading.Lock()


def season_ttl(season, current_ttl):
    """Past seasons never change, so they can be cached for a week; the current one can't."""
    return WEEK if int(season) < current_season() else current_ttl


def cached_api_get(path, ttl):
    """api_get with a per-request cache shared by every route (the league page, match sidebar and
    club page reuse each other's calls), so each distinct API call costs quota once per `ttl`.
    `ttl` may be a function of the response, e.g. long for finished matches, short for live ones.
    Concurrent identical requests wait for the first instead of each spending quota. Errors
    raise and are never cached."""
    key = f'api-football:{path}'
    cached = cache.get(key)
    if cached is not None:
        return cached

    with _inflight_guard:
        lock = _inflight_locks.setdefault(key, threading.Lock())
    with lock:
        cached = cache.get(key)
        if cached is not None:
            return cached
        response = api_get(path)
        cache.set(key, response, timeout=ttl(response) if callable(ttl) else ttl)
        return response
