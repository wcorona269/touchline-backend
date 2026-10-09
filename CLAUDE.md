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

## Performance pass (done)

- N+1s in `to_dict()` fixed: models now use declared relationships (eager via `lazy='joined'`
  for one-to-one, `lazy='selectin'` for collections) instead of redundant `User.query.get(...)`
  calls. `Notification.read_all()` does one bulk `UPDATE` instead of per-row commits.
  `PostLike`/`CommentLike.to_dict()` no longer fire a dead, unused query.
- Sports-data routes (`league.py`, `club.py`, `player.py`, `match.py`, `matches.py`,
  `standings.py`, `news.py`) are cached via `flask_caching` (`app/extensions.py`), with timeouts
  matched to how often that data changes (1hr league/player lookups, 5min standings/club info,
  30s–2min live/by-date matches, 10min news).
- Pagination added to `/notifications/fetch/<userId>` and `User.get_user_info` (profile
  posts/reposts/likes, 10 per page, exposed as `posts_total_pages`/`posts_current_page` etc. in
  the response — see matching frontend "See More" buttons in the frontend CLAUDE.md).

## Still unbounded (low risk, left as-is)

- `Favorite.get_user_favorites` returns a user's full favorites list unpaginated — left alone
  since favorites are a naturally small, user-curated list (confirmed via the frontend consumer,
  which renders them as a bounded chip list with no truncation).
