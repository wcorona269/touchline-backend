import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from app.routes import news_feeds
from app.routes.news_feeds import _published, mentions, personalized_news


def item(pub_date):
    return ET.fromstring(f'<item><pubDate>{pub_date}</pubDate></item>')


def test_gmt_and_numeric_offsets_are_taken_literally():
    assert _published(item('Fri, 16 Oct 2026 16:17:01 GMT')) == '2026-10-16T16:17:01Z'
    assert _published(item('Fri, 16 Oct 2026 16:17:01 +0000')) == '2026-10-16T16:17:01Z'
    assert _published(item('Fri, 16 Oct 2026 18:17:01 +0200')) == '2026-10-16T16:17:01Z'


def test_espn_est_label_is_read_as_new_york_local_time():
    # ESPN writes "EST" year-round; in October New York is on EDT (UTC-4), not EST (UTC-5).
    assert _published(item('Fri, 16 Oct 2026 15:12:49 EST')) == '2026-10-16T19:12:49Z'
    assert _published(item('Sun, 18 Jan 2026 15:12:49 EST')) == '2026-01-18T20:12:49Z'


def test_sky_bst_label_is_read_as_london_local_time():
    assert _published(item('Fri, 16 Oct 2026 18:30:00 BST')) == '2026-10-16T17:30:00Z'


def test_future_dates_are_clamped_to_now():
    future = (datetime.now(timezone.utc) + timedelta(days=1)).strftime('%a, %d %b %Y %H:%M:%S +0000')
    published = datetime.strptime(_published(item(future)), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    assert published <= datetime.now(timezone.utc)


def test_unparseable_dates_return_none():
    assert _published(item('not a date')) is None
    assert _published(ET.fromstring('<item/>')) is None


def article(title, published, description=''):
    return {'title': title, 'description': description, 'link': title, 'published': published, 'media': 'BBC Sport'}


def test_mentions_matches_whole_words_case_insensitively():
    assert mentions(article('Arsenal win again', ''), ['arsenal'])
    assert not mentions(article('Arsenalistas meet up', ''), ['Arsenal'])
    assert mentions(article('Derby report', '', 'Real Madrid were held'), ['Real Madrid'])


def test_personalized_news_puts_favorites_first_then_newest(monkeypatch):
    articles = [
        article('Chelsea sign striker', '2026-10-16T12:00:00Z'),
        article('Arsenal injury update', '2026-10-16T10:00:00Z'),
        article('Liverpool preview', '2026-10-16T11:00:00Z'),
    ]
    monkeypatch.setattr(news_feeds, 'general_news', lambda: articles)

    titles = [a['title'] for a in personalized_news(['Arsenal'])]

    assert titles == ['Arsenal injury update', 'Chelsea sign striker', 'Liverpool preview']


def sourced(title, media, published='2026-10-16T12:00:00Z'):
    return {**article(title, published), 'media': media}


def test_mix_sources_interleaves_publishers_newest_first_within_each_round():
    feed = [
        sourced('espn 1', 'ESPN', '2026-10-16T19:00:00Z'),
        sourced('espn 2', 'ESPN', '2026-10-16T19:00:00Z'),
        sourced('espn 3', 'ESPN', '2026-10-16T18:59:00Z'),
        sourced('guardian 1', 'The Guardian', '2026-10-16T18:00:00Z'),
        sourced('bbc 1', 'BBC Sport', '2026-10-16T16:00:00Z'),
        sourced('guardian 2', 'The Guardian', '2026-10-16T15:00:00Z'),
    ]

    titles = [a['title'] for a in news_feeds.mix_sources(feed)]

    assert titles == ['espn 1', 'guardian 1', 'bbc 1', 'espn 2', 'guardian 2', 'espn 3']


def test_mix_sources_keeps_every_article_once():
    feed = [sourced(f'{m} {i}', m) for i in range(3) for m in ('ESPN', 'BBC Sport')]
    assert sorted(a['title'] for a in news_feeds.mix_sources(feed)) == sorted(a['title'] for a in feed)
