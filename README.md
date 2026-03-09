# eBay Scraper

This project scrapes eBay search results and converts listing HTML into structured data files.

## What `ebay-dl.py` does

- Uses `argparse` to read a search term from the command line
- Uses `requests` to download eBay search result pages
- Uses `BeautifulSoup` (`bs4`) to parse listing data
- Extracts each item into a dictionary with keys:
  - `name`
  - `price` (integer cents)
  - `status`
  - `shipping` (integer cents, `0` for free shipping)
  - `free_returns` (boolean)
  - `items_sold` (integer)
- Writes output as JSON by default
- Supports CSV output with `--csv`

If a listing is missing a field, the key is still included and the value is `null` (or blank in CSV).

## Install Dependencies

```bash
python3 -m pip install requests beautifulsoup4


```md
## How to run

```bash
python3 ebay-dl.py "drill press"
python3 ebay-dl.py "mechanical keyboard"
python3 ebay-dl.py "spiderman comic"

And (extra credit):

```md
## CSV (extra credit)

```bash
python3 ebay-dl.py "drill press" --csv
python3 ebay-dl.py "mechanical keyboard" --csv
python3 ebay-dl.py "spiderman comic" --csv

## Course Project
[CMC CSCI040 Project 02](https://github.com/mikeizbicki/cmc-csci040/tree/2026spring/project_02_webscraping)
