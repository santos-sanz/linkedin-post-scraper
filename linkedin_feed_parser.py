import json
import sys
import html as html_lib
import re
from bs4 import BeautifulSoup


def parse_posts(html: str):
    """Parse LinkedIn feed HTML and return a list of posts."""
    soup = BeautifulSoup(html, 'html.parser')
    posts = []

    # Feed data is embedded inside <code> tags with id like `bpr-guid-XXXX`.
    for code in soup.find_all('code', id=re.compile(r'^bpr-guid-')):
        try:
            data = json.loads(html_lib.unescape(code.get_text() or ''))
        except Exception:
            continue

        feed = (
            data.get('data', {})
            .get('data', {})
            .get('feedDashMainFeedByMainFeed')
        )
        if not feed or '*elements' not in feed:
            continue

        index = {
            item['entityUrn']: item
            for item in data.get('included', [])
            if isinstance(item, dict) and 'entityUrn' in item
        }

        for urn in feed.get('*elements', []):
            item = index.get(urn)
            if not item:
                continue

            post = {}

            # Basic identifiers
            meta = item.get('metadata') or {}
            post_id = meta.get('shareUrn') or item.get('entityUrn')
            if post_id:
                post['id'] = post_id

            actor_data = item.get('actor') or {}
            actor = actor_data.get('name', {}).get('text')
            if actor:
                post['author'] = actor
            author_url = (actor_data.get('navigationContext') or {}).get('actionTarget')
            if author_url:
                post['author_url'] = author_url

            commentary = item.get('commentary', {}).get('text')
            if isinstance(commentary, dict):
                commentary = commentary.get('text')
            if commentary:
                post['text'] = commentary

            header = (
                (item.get('contextualHeader') or item.get('header') or {})
                .get('text', {})
                .get('text')
            )
            if header:
                post['header'] = header

            # Try to locate a timestamp value for the post
            timestamp = None
            for key in (
                'createdAt',
                'publishedAt',
                'lastModifiedAt',
                'createdTime',
                'publishedTime',
            ):
                value = item.get(key)
                if isinstance(value, int):
                    timestamp = value
                    break
            if timestamp is None:
                meta = item.get('metadata') or {}
                for key in ('createdAt', 'publishedAt', 'time'):
                    value = meta.get(key)
                    if isinstance(value, int):
                        timestamp = value
                        break
            if timestamp is None and '*attachment' in item:
                att = index.get(item['*attachment']) or {}
                for key in ('createdAt', 'publishedAt', 'time'):
                    value = att.get(key)
                    if isinstance(value, int):
                        timestamp = value
                        break
            from datetime import datetime, timezone
            if timestamp is not None:
                # convert to ISO date; timestamps are milliseconds
                if timestamp > 1e12:  # likely ms
                    timestamp /= 1000
                post['published_at'] = datetime.fromtimestamp(
                    timestamp, tz=timezone.utc
                ).isoformat()
            else:
                # if no timestamp was found, set current time to avoid null values
                post['published_at'] = datetime.now(timezone.utc).isoformat()

            # Social engagement counts
            social = index.get(item.get('*socialDetail')) if '*socialDetail' in item else None
            counts = index.get(social.get('*totalSocialActivityCounts')) if isinstance(social, dict) else None
            if counts:
                if isinstance(counts.get('numLikes'), int):
                    post['like_count'] = counts['numLikes']
                if isinstance(counts.get('numComments'), int):
                    post['comment_count'] = counts['numComments']
                if isinstance(counts.get('numShares'), int):
                    post['share_count'] = counts['numShares']
                rcounts = counts.get('reactionTypeCounts')
                if isinstance(rcounts, list):
                    post['reaction_counts'] = {
                        r.get('reactionType'): r.get('count')
                        for r in rcounts
                        if isinstance(r, dict) and r.get('reactionType') and isinstance(r.get('count'), int)
                    }

            if post:
                posts.append(post)

    return posts


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Parse LinkedIn feed HTML and output JSON of posts.')
    parser.add_argument('html_file', help='Path to HTML file (use - for stdin)')
    args = parser.parse_args()

    html_data = sys.stdin.read() if args.html_file == '-' else open(args.html_file, encoding='utf-8').read()
    posts = parse_posts(html_data)
    json.dump(posts, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write('\n')
