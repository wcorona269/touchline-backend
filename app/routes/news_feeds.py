"""Football news from publisher RSS feeds.

Replaces the GoogleNews scraping library, which stopped returning anything once Google started
rate-limiting (HTTP 429) the server's IP. Publisher feeds are free, keyless, fast and stable.
Each feed is fetched at most once per FEED_TTL and shared by every request; per-user filtering
(favorites, club, league) happens on the cached articles, so personalization costs nothing.
"""
import logging
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from zoneinfo import ZoneInfo

from ..extensions import cache

logger = logging.getLogger(__name__)

FEED_TTL = 600
USER_AGENT = 'Mozilla/5.0 (compatible; TouchlineNews/1.0)'
MEDIA_NS = '{http://search.yahoo.com/mrss/}'

GENERAL_FEEDS = {
    'BBC Sport': 'https://feeds.bbci.co.uk/sport/football/rss.xml',
    'The Guardian': 'https://www.theguardian.com/football/rss',
    'ESPN': 'https://www.espn.com/espn/rss/soccer/news',
    'Sky Sports': 'https://www.skysports.com/rss/11095',
}

# api-sports league id -> Guardian section slug, for the leagues the Guardian covers directly.
GUARDIAN_LEAGUE_SLUGS = {
    39: 'premierleague',
    140: 'laligafootball',
    135: 'serieafootball',
    78: 'bundesligafootball',
    61: 'ligue1football',
    2: 'championsleague',
    253: 'mls',
}

# api-sports club names whose Guardian slug isn't just the name hyphenated or joined.
GUARDIAN_CLUB_SLUGS = {
    'Tottenham': 'tottenham-hotspur',
    'Leeds': 'leedsunited',
    'Newcastle': 'newcastleunited',
    'Ipswich': 'ipswichtown',
}


def _image(item):
    candidates = item.findall(f'{MEDIA_NS}content') + item.findall(f'{MEDIA_NS}thumbnail')
    candidates = [c for c in candidates if c.get('url')]
    if candidates:
        return max(candidates, key=lambda c: int(c.get('width') or 0)).get('url')
    enclosure = item.find('enclosure')
    if enclosure is not None and (enclosure.get('type') or '').startswith('image'):
        return enclosure.get('url')
    return None


# Feeds stamp local times with zone abbreviations that don't track daylight saving (ESPN writes
# "EST" year-round) or that the email date parser doesn't know ("BST"). Read them as the region's
# actual local time instead.
REGIONAL_ZONES = {
    'EST': 'America/New_York', 'EDT': 'America/New_York',
    'BST': 'Europe/London',
}


def _published(item):
    raw = (item.findtext('pubDate') or '').strip()
    try:
        abbreviation = raw.rsplit(' ', 1)[-1]
        if abbreviation in REGIONAL_ZONES:
            published = parsedate_to_datetime(raw.rsplit(' ', 1)[0]).replace(tzinfo=ZoneInfo(REGIONAL_ZONES[abbreviation]))
        else:
            published = parsedate_to_datetime(raw)
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
        published = published.astimezone(timezone.utc)
    except (TypeError, ValueError, IndexError):
        return None
    # Live blogs are sometimes dated at a future kickoff time; don't let them pin the top of the feed.
    return min(published, datetime.now(timezone.utc)).strftime('%Y-%m-%dT%H:%M:%SZ')


def _clean(text):
    return re.sub(r'<[^>]+>', '', unescape(text or '')).strip()


@cache.memoize(timeout=FEED_TTL)
def fetch_feed(source, url):
    """Articles from one RSS feed. Failures return [] (and are cached) rather than raising,
    so one broken feed never takes down the rest."""
    try:
        request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        root = ET.fromstring(urllib.request.urlopen(request, timeout=8).read())
    except urllib.error.HTTPError as e:
        # Guessed Guardian club slugs are expected to 404 sometimes.
        log = logger.debug if e.code == 404 else logger.warning
        log('News feed %s (%s) failed: %s', source, url, e)
        return []
    except (urllib.error.URLError, ET.ParseError, TimeoutError) as e:
        logger.warning('News feed %s (%s) failed: %s', source, url, e)
        return []

    articles = []
    for item in root.iter('item'):
        title, link = _clean(item.findtext('title')), item.findtext('link')
        if not title or not link:
            continue
        articles.append({
            'title': title,
            'description': _clean(item.findtext('description'))[:280],
            'link': link.strip(),
            'media': source,
            'img': _image(item),
            'published': _published(item),
        })
    return articles


def _newest_first(articles):
    # Several feeds can carry the same story; keep one copy per link.
    unique = {a['link']: a for a in articles}
    return sorted(unique.values(), key=lambda a: a['published'] or '', reverse=True)


def general_news():
    articles = []
    for source, url in GENERAL_FEEDS.items():
        articles.extend(fetch_feed(source, url))
    return _newest_first(articles)


def mentions(article, terms):
    text = f"{article['title']} {article['description']}"
    return any(re.search(rf'\b{re.escape(term)}\b', text, re.IGNORECASE) for term in terms if term)


def personalized_news(fav_names, limit=100):
    """Newest-first general news, with stories mentioning the user's favorites moved to the top."""
    articles = general_news()
    if not fav_names:
        return articles[:limit]
    favorite = [a for a in articles if mentions(a, fav_names)]
    rest = [a for a in articles if not mentions(a, fav_names)]
    return (favorite + rest)[:limit]


def _guardian_slugs(club_name):
    if club_name in GUARDIAN_CLUB_SLUGS:
        return [GUARDIAN_CLUB_SLUGS[club_name]]
    words = re.findall(r'[a-z0-9]+', club_name.lower().replace('&', 'and'))
    return list(dict.fromkeys(['-'.join(words), ''.join(words)]))


def club_news(club_name, limit=25):
    articles = []
    for slug in _guardian_slugs(club_name):
        found = fetch_feed('The Guardian', f'https://www.theguardian.com/football/{slug}/rss')
        if found:
            articles.extend(found)
            break
    articles.extend(a for a in general_news() if mentions(a, [club_name]))
    return _newest_first(articles)[:limit]


def league_news(league_id, league_name, limit=25):
    articles = []
    slug = GUARDIAN_LEAGUE_SLUGS.get(int(league_id))
    if slug:
        articles.extend(fetch_feed('The Guardian', f'https://www.theguardian.com/football/{slug}/rss'))
    articles.extend(a for a in general_news() if mentions(a, [league_name]))
    return _newest_first(articles)[:limit]
