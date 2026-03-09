# eBay Scraper

This project scrapes eBay search results and converts listing HTML into structured data files.

## What `ebay-dl.py` does

- Uses `argparse` to read a search term from the command line
- Uses `selenium` to download eBay search result pages (eBay blocks the `requests` library with a CAPTCHA, so selenium is used to open a real Chrome browser instead)
- Uses `BeautifulSoup` (`bs4`) to parse listing data
- Extracts each item into a dictionary with keys: `name`, `price` (integer cents), `status`, `shipping` (integer cents, `0` for free), `free_returns` (boolean), `items_sold` (integer)
- Writes output as JSON by default, or CSV with `--csv`

## Install Dependencies
```bash
python3 -m python3 -m pip install requests beautifulsoup4
```

## How to Run
```bash
python3 ebay-dl.py "drill press"
python3 ebay-dl.py "mechanical keyboard"
python3 ebay-dl.py "spiderman comic"
```

## CSV Output (Extra Credit)
```bash
python3 ebay-dl.py "drill press" --csv
python3 ebay-dl.py "mechanical keyboard" --csv
python3 ebay-dl.py "spiderman comic" --csv
```

## Course Project

[CMC CSCI040 Project 02](https://github.com/mikeizbicki/cmc-csci040/tree/2026spring/project_02_webscraping)
