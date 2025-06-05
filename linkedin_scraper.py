import argparse
import json
import sys

from autoparse import autoparse_html
from linkedin_feed_parser import parse_posts


def main():
    parser = argparse.ArgumentParser(
        description="Extract structured data and posts from LinkedIn HTML"
    )
    parser.add_argument("html_file", help="HTML file to parse (- for stdin)")
    parser.add_argument("--url", default="", help="Base URL of the page")
    args = parser.parse_args()

    html_data = (
        sys.stdin.read()
        if args.html_file == "-"
        else open(args.html_file, encoding="utf-8").read()
    )

    structured = autoparse_html(html_data, url=args.url)
    posts = parse_posts(html_data)

    result = {"structured_data": structured, "posts": posts}
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
