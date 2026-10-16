import threading
import time

import pytest

import app as app_module
from app.routes import club, league
from app.routes.slim import slim_fixture, slim_league_entry

DELAY = 0.2


def fixture(fixture_id, league_id, league_name):
    team = lambda i: {'id': i, 'name': f'Team {i}', 'logo': 'x.png', 'winner': None}
    return {
        'fixture': {'id': fixture_id, 'date': '2026-10-17T14:00:00+00:00', 'timezone': 'UTC', 'referee': 'Ref',
                    'status': {'short': 'NS', 'long': 'Not Started', 'elapsed': None},
                    'venue': {'id': 1, 'name': 'Ground', 'city': 'Town'}, 'periods': {'first': None}},
        'league': {'id': league_id, 'name': league_name, 'country': 'England', 'logo': 'l.png', 'flag': 'f.svg',
                   'season': 2026, 'round': 'Regular Season - 8', 'standings': True},
        'teams': {'home': team(1), 'away': team(2)},
        'goals': {'home': None, 'away': None},
        'score': {'halftime': {'home': None, 'away': None}, 'fulltime': {'home': None, 'away': None}},
        'events': [{'type': 'Goal'}],
    }


@pytest.fixture()
def slow_api(monkeypatch):
    """Fake cached_api_get: every call takes DELAY seconds; tracks peak concurrency."""
    state = {'active': 0, 'peak': 0, 'calls': []}
    lock = threading.Lock()

    def fake(path, ttl):
        with lock:
            state['active'] += 1
            state['peak'] = max(state['peak'], state['active'])
            state['calls'].append(path)
        time.sleep(DELAY)
        with lock:
            state['active'] -= 1
        if path.startswith('/teams?id='):
            return [{'team': {'id': 42, 'name': 'Arsenal'}, 'venue': {}}]
        if path.startswith('/players/squads'):
            return [{'players': []}]
        if path.startswith('/fixtures'):
            return [fixture(1, 39, 'Premier League'), fixture(2, 2, 'UEFA Champions League'), fixture(3, 39, 'Premier League')]
        if path.startswith('/teams/statistics'):
            return {'league': {'id': 39, 'name': 'Premier League'}} if 'league=39' in path else []
        if path.startswith('/standings'):
            return [{'league': {'id': 39, 'name': 'Premier League', 'standings': [[]]}}]
        return []

    monkeypatch.setattr(club, 'cached_api_get', fake)
    monkeypatch.setattr(league, 'cached_api_get', fake)
    monkeypatch.setattr(club, 'club_news', lambda name: [{'title': f'{name} news'}])
    monkeypatch.setattr(league, 'league_news', lambda league_id, name: [{'title': f'{name} news'}])
    return state


def test_club_route_fetches_in_parallel(slow_api):
    client = app_module.app.test_client()
    start = time.monotonic()
    body = client.get('/clubs/info/42/2026').get_json()
    elapsed = time.monotonic() - start

    # 3 base calls + 2 competitions' stats = 5 calls; sequential would take ~5 * DELAY.
    assert len(slow_api['calls']) == 5
    assert slow_api['peak'] >= 2
    assert elapsed < 3 * DELAY
    # Results land in the right fields; the competition with no stats yet is dropped.
    assert body['club'][0]['team']['name'] == 'Arsenal'
    assert [s['league']['id'] for s in body['stats']] == [39]
    assert body['news'] == [{'title': 'Arsenal news'}]
    assert 'events' not in body['fixtures'][0] and 'score' not in body['fixtures'][0]


def test_league_route_fetches_in_parallel(slow_api):
    client = app_module.app.test_client()
    start = time.monotonic()
    body = client.get('/leagues/39/2026').get_json()
    elapsed = time.monotonic() - start

    assert len(slow_api['calls']) == 4
    assert slow_api['peak'] == 4
    assert elapsed < 2 * DELAY
    assert body['news'] == [{'title': 'Premier League news'}]
    assert len(body['fixtures']) == 3 and 'events' not in body['fixtures'][0]


def test_slim_fixture_keeps_what_the_ui_reads():
    slim = slim_fixture(fixture(7, 39, 'Premier League'))
    assert slim['fixture']['id'] == 7
    assert slim['fixture']['status']['short'] == 'NS'
    assert slim['fixture']['venue'] == {'name': 'Ground', 'city': 'Town'}
    assert slim['league'] == {'id': 39, 'name': 'Premier League', 'country': 'England', 'logo': 'l.png',
                              'flag': 'f.svg', 'season': 2026, 'round': 'Regular Season - 8'}
    assert slim['teams']['home'] == {'id': 1, 'name': 'Team 1', 'logo': 'x.png', 'winner': None}
    assert slim['goals'] == {'home': None, 'away': None}
    assert set(slim) == {'fixture', 'league', 'teams', 'goals'}


def test_slim_league_entry_drops_season_history():
    entry = {'league': {'id': 39, 'name': 'Premier League', 'type': 'League', 'logo': 'l.png'},
             'country': {'name': 'England', 'code': 'GB-ENG', 'flag': 'f.svg'},
             'seasons': [{'year': y, 'coverage': {}} for y in range(2010, 2027)]}
    assert slim_league_entry(entry) == {'league': entry['league'], 'country': entry['country']}
