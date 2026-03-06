# eBay Scraper

This script scrapes eBay search results and saves them as a JSON file.

## Note
eBay's bot detection blocks the `requests` library and returns a CAPTCHA page. `selenium` is used instead to fetch pages, which opens a real Chrome browser to bypass the bot detection.

## How to Run
```bash
python3 ebay-dl.py "spiderman comic"
python3 ebay-dl.py "mechanical keyboard"
python3 ebay-dl.py "drill press"
```

## CSV Output (optional)
```bash
python3 ebay-dl.py "spiderman comic" --csv
```

## Course Project
[CMC CSCI040 Project 02](https://github.com/mikeizbicki/cmc-csci040/tree/2026spring/project_02_webscraping)