from datetime import datetime


def current_season():
    # European seasons start in late summer, so before July we're still in last year's season.
    now = datetime.utcnow()
    return now.year if now.month >= 7 else now.year - 1
