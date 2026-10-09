import re
from datetime import datetime, timezone
from app.models.db import db
from app.models.post_model import Post
from app.models.like_model import PostLike
from app.models.repost_model import Repost

ISO_UTC_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')


def test_create_post(app, make_user):
    user = make_user('poster1')
    success, data = Post.create_post(user.id, 'hello world')
    assert success is True
    assert data['text'] == 'hello world'
    assert data['username'] == 'poster1'


def test_post_to_dict_uses_relationship_not_requery(app, make_user):
    # regression check for the N+1 fix: to_dict() should read self.user
    # rather than re-querying, and still produce the same shape.
    user = make_user('poster2')
    success, data = Post.create_post(user.id, 'another post')
    post = Post.query.get(data['id'])

    result = post.to_dict()
    assert result['username'] == 'poster2'
    assert result['avatar_url'] == user.avatar_url
    assert result['likes'] == []
    assert result['comments'] == []
    assert result['reposts'] == []


def test_post_to_dict_includes_likes_and_reposts(app, make_user):
    user = make_user('poster3')
    other = make_user('otheruser3')
    _, data = Post.create_post(user.id, 'liked and reposted')
    post = Post.query.get(data['id'])

    PostLike.add_like(other.id, post.id)
    Repost.add_repost(other.id, post.id)

    result = Post.query.get(post.id).to_dict()
    assert len(result['likes']) == 1
    assert len(result['reposts']) == 1
    assert result['reposts'][0]['username'] == 'otheruser3'


def test_delete_post(app, make_user):
    user = make_user('poster4')
    _, data = Post.create_post(user.id, 'to be deleted')
    assert Post.delete_post(data['id']) is True
    assert Post.query.get(data['id']) is None


def test_delete_post_missing_returns_false(app):
    assert Post.delete_post(999999) is False


def test_created_at_is_valid_iso8601_utc(app, make_user):
    # Regression check: created_at columns are naive (no tz awareness), so
    # whatever wall-clock value Postgres writes depends on the session's
    # TimeZone setting at INSERT time - if that session isn't forced to
    # UTC (see db.py's "connect" event listener), this value silently
    # drifts by the server's UTC offset while still being labeled 'Z',
    # and sort-by-created_at on the frontend becomes unreliable whenever
    # the DB session timezone differs from what the string claims.
    user = make_user('tzchecker')
    _, data = Post.create_post(user.id, 'tz regression check')

    assert ISO_UTC_RE.match(data['created_at']), (
        f"created_at {data['created_at']!r} is not valid ISO 8601 UTC "
        "('T' separator + 'Z' suffix) - browsers parse other formats "
        "inconsistently, which breaks created_at-based sorting."
    )

    parsed = datetime.strptime(data['created_at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    drift_seconds = abs((datetime.now(timezone.utc) - parsed).total_seconds())
    assert drift_seconds < 60, (
        f"created_at is {drift_seconds:.0f}s off from real UTC now - the "
        "DB session that wrote this row likely wasn't forced to UTC."
    )
