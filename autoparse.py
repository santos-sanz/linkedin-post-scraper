import argparse
import json
import sys

import extruct
from w3lib.html import get_base_url


def autoparse_html(html: str, url: str = "") -> dict:
    """Extract structured data like JSON-LD, microdata and OpenGraph."""
    base_url = get_base_url(html, url)
    data = extruct.extract(
        html,
        base_url=base_url,
        syntaxes=["json-ld", "microdata", "opengraph", "rdfa"],
    )
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Parse structured data from HTML using extruct "
            "(ZenRows autoparse clone)."
        )
    )
    parser.add_argument("html_file", help="HTML file to parse (- for stdin)")
    parser.add_argument("--url", default="", help="Base URL of the page")
    args = parser.parse_args()

    html = (
        sys.stdin.read()
        if args.html_file == "-"
        else open(args.html_file, encoding="utf-8").read()
    )
    data = autoparse_html(html, url=args.url)
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
