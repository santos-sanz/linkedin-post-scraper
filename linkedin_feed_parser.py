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
            actor = item.get('actor', {}).get('name', {}).get('text')
            if actor:
                post['author'] = actor

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
                post['published_at'] = None

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
