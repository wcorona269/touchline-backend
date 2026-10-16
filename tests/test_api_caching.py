import threading
import time
from datetime import date, timedelta

import pytest
from cachelib import SimpleCache

from app.routes import api_football
from app.routes.api_football import ApiFootballError, cached_api_get, season_ttl, HOUR, MINUTE, WEEK
from app.routes.match import match_ttl
from app.routes.matches import date_ttl
from app.routes.seasons import current_season


@pytest.fixture()
def api(monkeypatch):
    """A real in-memory cache plus a fake api_get that records calls and remembers TTLs."""
    store = SimpleCache()
    ttls = {}
    original_set = store.set

    def recording_set(key, value, timeout=None):
        ttls[key] = timeout
        return original_set(key, value, timeout=timeout)

    store.set = recording_set
    calls = []
    responses = {}

    def fake_api_get(path, conn=None):
        calls.append(path)
        result = responses[path]
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(api_football, 'cache', store)
    monkeypatch.setattr(api_football, 'api_get', fake_api_get)
    return calls, responses, ttls


def test_repeat_requests_hit_the_cache(api):
    calls, responses, _ = api
    responses['/standings?league=39&season=2026'] = [{'league': 'PL'}]

    assert cached_api_get('/standings?league=39&season=2026', MINUTE) == [{'league': 'PL'}]
    assert cached_api_get('/standings?league=39&season=2026', MINUTE) == [{'league': 'PL'}]
    assert calls == ['/standings?league=39&season=2026']


def test_empty_successful_responses_are_cached(api):
    calls, responses, _ = api
    responses['/fixtures?date=2020-01-01'] = []

    cached_api_get('/fixtures?date=2020-01-01', WEEK)
    cached_api_get('/fixtures?date=2020-01-01', WEEK)
    assert len(calls) == 1


def test_errors_are_not_cached(api):
    calls, responses, _ = api
    responses['/teams?id=42'] = ApiFootballError({'rateLimit': 'Too many requests'})

    with pytest.raises(ApiFootballError):
        cached_api_get('/teams?id=42', HOUR)
    responses['/teams?id=42'] = [{'team': 'Arsenal'}]
    assert cached_api_get('/teams?id=42', HOUR) == [{'team': 'Arsenal'}]
    assert len(calls) == 2


def test_ttl_can_depend_on_the_response(api):
    _, responses, ttls = api
    responses['/fixtures?id=1'] = [{'fixture': {'status': {'short': 'FT'}}}]

    cached_api_get('/fixtures?id=1', match_ttl)
    assert ttls['api-football:/fixtures?id=1'] == WEEK


def test_concurrent_identical_requests_share_one_call(api, monkeypatch):
    calls, responses, _ = api
    responses['/fixtures?live=all'] = []
    real_fake = api_football.api_get

    def slow_api_get(path, conn=None):
        time.sleep(0.05)
        return real_fake(path)

    monkeypatch.setattr(api_football, 'api_get', slow_api_get)
    threads = [threading.Thread(target=cached_api_get, args=('/fixtures?live=all', MINUTE)) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert calls == ['/fixtures?live=all']


def test_past_seasons_are_cached_for_a_week():
    assert season_ttl(current_season() - 1, MINUTE) == WEEK
    assert season_ttl(current_season(), MINUTE) == MINUTE


def test_match_ttl_by_status():
    status = lambda s: [{'fixture': {'status': {'short': s}}}]
    assert match_ttl(status('FT')) == WEEK
    assert match_ttl(status('NS')) == 10 * MINUTE
    assert match_ttl(status('PST')) == 10 * MINUTE
    assert match_ttl(status('2H')) == MINUTE
    assert match_ttl([]) == MINUTE


def test_date_ttl():
    today = date.today()
    assert date_ttl((today - timedelta(days=3)).isoformat()) == WEEK
    assert date_ttl((today - timedelta(days=1)).isoformat()) == 2 * MINUTE
    assert date_ttl(today.isoformat()) == 2 * MINUTE
    assert date_ttl((today + timedelta(days=2)).isoformat()) == 30 * MINUTE
    assert date_ttl('not-a-date') == 2 * MINUTE
