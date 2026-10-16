# touchline_prod/backend — Touchline API

Flask API backend for Touchline (soccer stats + Twitter-style social timeline). Postgres via
SQLAlchemy, Alembic for migrations. Deployed to Azure (`.github/workflows/*touchline-api*`,
`*touchline-backend*`).

## Layout

- `app/models/` — ORM models: users, posts, comments, likes (post/comment), reposts,
  favorites, notifications.
- `app/routes/` — API endpoints, including sports-data routes that proxy/aggregate from the
  api-sports.io football API (league, club, player, match, standings) plus a news route.
- `app/routes/api_football.py` — `api_get` helper for api-sports calls. The free plan allows
  10 requests/minute and 100/day, and reports failures as HTTP 200 with an `errors` field;
  `api_get` raises on those, and routes use `response_filter=is_success` so errors aren't cached.
- `app/routes/news_feeds.py` — news from publisher RSS feeds (BBC, Guardian, ESPN, Sky), cached
  per feed and filtered per request. Replaced the GoogleNews scraper after Google began
  rate-limiting (429) the server's IP.
- `app/routes/seasons.py` — `current_season()` (July rollover); don't hardcode seasons.
- `database.py`, `config.py`, `run.py` — app/DB setup and entrypoint.
- `migrations/` — Alembic schema history.
- `seeds.py` — dev seed data.

`/Users/Will2/Desktop/touchline_soccer/flask-server` was an earlier iteration of this same
backend; it has been removed as a superseded duplicate — this folder is the only copy.

## Performance pass (done)

- N+1s in `to_dict()` fixed: models now use declared relationships (eager via `lazy='joined'`
  for one-to-one, `lazy='selectin'` for collections) instead of redundant `User.query.get(...)`
  calls. `Notification.read_all()` does one bulk `UPDATE` instead of per-row commits.
  `PostLike`/`CommentLike.to_dict()` no longer fire a dead, unused query.
- api-sports calls go through `cached_api_get` (`app/routes/api_football.py`): cached per call
  path, shared across routes, with TTLs by data type (1 day club info, 12h squads, 1h stats/top
  scorers, 10 min current standings/fixtures, 1 week past seasons and finished matches, 60s live).
  Concurrent identical calls are coalesced. Cache is `FileSystemCache` (`CACHE_DIR`), so it
  survives restarts; tests use `NullCache`. News feeds are memoized per feed (10 min).
- Pagination added to `/notifications/fetch/<userId>` and `User.get_user_info` (profile
  posts/reposts/likes, 10 per page, exposed as `posts_total_pages`/`posts_current_page` etc. in
  the response — see matching frontend "See More" buttons in the frontend CLAUDE.md).

## Still unbounded (low risk, left as-is)

- `Favorite.get_user_favorites` returns a user's full favorites list unpaginated — left alone
  since favorites are a naturally small, user-curated list (confirmed via the frontend consumer,
  which renders them as a bounded chip list with no truncation).
