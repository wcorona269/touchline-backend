import json
import os
import http.client
from dotenv import load_dotenv
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
