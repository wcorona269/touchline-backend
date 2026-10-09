# touchline_prod/backend — Touchline API

Flask API backend for Touchline (soccer stats + Twitter-style social timeline). Postgres via
SQLAlchemy, Alembic for migrations. Deployed to Azure (`.github/workflows/*touchline-api*`,
`*touchline-backend*`).

## Layout

- `app/models/` — ORM models: users, posts, comments, likes (post/comment), reposts,
  favorites, notifications.
- `app/routes/` — API endpoints, including sports-data routes that proxy/aggregate from the
  api-sports.io football API (league, club, player, match, standings) plus a news-scraping route.
- `database.py`, `config.py`, `run.py` — app/DB setup and entrypoint.
- `migrations/` — Alembic schema history.
- `seeds.py` — dev seed data.

`/Users/Will2/Desktop/touchline_soccer/flask-server` was an earlier iteration of this same
backend; it has been removed as a superseded duplicate — this folder is the only copy.

## Known performance hotspots (not yet fixed)

- **N+1 queries in `to_dict()` methods**: `Post`, `Comment`, `PostLike`/`CommentLike`,
  `Notification`, and `Repost` models all call `User.query.get(...)` or walk lazy
  (`lazy='select'`) relationships inside `to_dict()` instead of eager-loading. A single page of
  10 posts can trigger 100+ queries. No route uses `joinedload`/`.options(...)`.
- `Notification.read_all()` commits inside a per-notification loop instead of one bulk update.
- Unpaginated/unbounded queries: notification fetch, `Notification.read_all`,
  `User.get_user_info` (full post/repost/like history), favorites fetch.
- **Uncached synchronous third-party API calls** in request handlers — `league.py`, `club.py`
  (worst: 4 sequential calls plus a per-competition loop re-calling the API), `player.py`,
  `match.py`, `matches.py`, `standings.py`, `news.py`. `flask_caching.Cache` is already
  configured in `app/__init__.py` but only used on one endpoint — caching the sports-data routes
  is the highest-leverage fix since that data changes rarely.
