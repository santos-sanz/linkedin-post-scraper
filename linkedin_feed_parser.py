import json
from bs4 import BeautifulSoup
import sys


def parse_posts(html: str):
    """Parse LinkedIn feed HTML and return a list of posts."""
    soup = BeautifulSoup(html, 'html.parser')
    posts = []
    # LinkedIn posts often contain these class names
    for article in soup.select('div.feed-shared-update-v2, div.occludable-update, div.feed-shared-update'):  # common containers
        post = {}
        author_tag = article.select_one('.feed-shared-actor__name, .update-components-actor__title')
        if author_tag:
            post['author'] = author_tag.get_text(strip=True)
        text_tag = article.select_one('.feed-shared-update-v2__description, .update-components-text, .feed-shared-text')
        if text_tag:
            post['text'] = text_tag.get_text("\n", strip=True)
        like_tag = article.select_one('[data-test-like-count]')
        if like_tag:
            post['likes'] = like_tag.get_text(strip=True)
        comment_tag = article.select_one('[data-test-comment-count]')
        if comment_tag:
            post['comments'] = comment_tag.get_text(strip=True)
        timestamp_tag = article.select_one('span.feed-shared-actor__sub-description span.visually-hidden, time')
        if timestamp_tag:
            post['timestamp'] = timestamp_tag.get_text(strip=True)
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
