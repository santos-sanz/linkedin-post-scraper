# LinkedIn Post Scraper

This repository contains a simple scraper to gather posts from LinkedIn. The scraper relies on standard Python libraries for web scraping.

## Setup

1. Clone the repository.
2. Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Usage

Implement your scraping logic inside the project using your preferred tools. The dependencies listed will help parse HTML pages retrieved from LinkedIn. Remember that scraping LinkedIn may violate their Terms of Service, so proceed responsibly.

### Autoparse helper

The script `autoparse.py` mimics the behaviour of the [ZenRows autoparse](https://www.zenrows.com/) feature. It extracts structured data such as JSON‑LD, Microdata, RDFa and OpenGraph from a given HTML file.

Run it with an HTML file or with `-` to read from standard input:

```bash
python autoparse.py 'Feed _ LinkedIn.html'
```

It outputs a JSON document with the data that was found.

### Combined scraper

`linkedin_scraper.py` merges the autoparse functionality with the feed parser so
you can extract both structured data and individual posts in one step:

```bash
python linkedin_scraper.py 'Feed _ LinkedIn.html'
```

The output is a single JSON object containing the parsed structured data under
`structured_data` and a list of posts under `posts`.

## Files

- `requirements.txt` – Python dependencies.
- `Feed _ LinkedIn.html` – Example HTML file provided as part of the repository.
- `linkedin_scraper.py` – Combined script that outputs structured data and posts.

Feel free to extend the project and contribute improvements.
