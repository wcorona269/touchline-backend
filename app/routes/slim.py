"""Trim api-sports objects down to the fields the frontend renders. The raw objects carry a lot
the UI never reads (per-fixture score breakdowns and event logs, every season a league has ever
had with its coverage flags), which made some responses hundreds of KB to a few MB."""


def _pick(obj, keys):
    return {key: obj[key] for key in keys if key in (obj or {})}


def slim_team(team):
    return _pick(team, ('id', 'name', 'logo', 'winner'))


def slim_fixture(fixture):
    """For fixture lists and cards. The single-match page uses the full object instead."""
    return {
        'fixture': {
            **_pick(fixture['fixture'], ('id', 'date', 'timezone', 'status', 'referee')),
            'venue': _pick(fixture['fixture'].get('venue'), ('name', 'city')),
        },
        'league': _pick(fixture['league'], ('id', 'name', 'country', 'logo', 'flag', 'season', 'round')),
        'teams': {side: slim_team(fixture['teams'][side]) for side in ('home', 'away')},
        'goals': fixture['goals'],
    }


def slim_fixtures(fixtures):
    return [slim_fixture(f) for f in fixtures]


def slim_league_entry(entry):
    """A /leagues entry without its full season history."""
    return {
        'league': _pick(entry['league'], ('id', 'name', 'type', 'logo')),
        'country': _pick(entry['country'], ('name', 'code', 'flag')),
    }
