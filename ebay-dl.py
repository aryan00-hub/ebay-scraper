import argparse
import csv
import json
import re
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.ebay.com/sch/i.html"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}


def parse_money_to_cents(text):
    if not text:
        return None
    m = re.search(r"(\d[\d,]*)(?:\.(\d{1,2}))?", text)
    if not m:
        return None
    dollars = int(m.group(1).replace(",", ""))
    cents = int((m.group(2) or "0").ljust(2, "0")[:2])
    return dollars * 100 + cents


def parse_items_sold(text):
    if not text:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)\s*([KMB]?)\s*sold", text, re.I)
    if not m:
        return None
    val = float(m.group(1))
    suffix = m.group(2).upper()
    mult = 1
    if suffix == "K":
        mult = 1_000
    elif suffix == "M":
        mult = 1_000_000
    elif suffix == "B":
        mult = 1_000_000_000
    return int(val * mult)


def fetch_page(session, search_term, page_num, retries=4):
    params = {"_nkw": search_term, "_pgn": page_num}
    for attempt in range(retries):
        r = session.get(BASE_URL, params=params, timeout=25)
        r.raise_for_status()
        html = r.text
        if "Pardon Our Interruption" not in html:
            return html
        time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Blocked by eBay on page {page_num}")


def parse_card(card):
    item = {
        "name": None,
        "price": None,
        "status": None,
        "shipping": None,
        "free_returns": None,
        "items_sold": None,
    }

    title = card.select_one(".s-card__title, .s-item__title")
    if title:
        name = title.get_text(" ", strip=True)
        name = re.sub(r"\s*Opens in a new window or tab\s*$", "", name, flags=re.I)
        if name.lower() != "shop on ebay":
            item["name"] = name

    price = card.select_one(".s-card__price, .s-item__price")
    if price:
        item["price"] = parse_money_to_cents(price.get_text(" ", strip=True))

    rows = card.select(".s-card__attribute-row, .s-item__detail")
    all_text = " ".join(r.get_text(" ", strip=True) for r in rows) or card.get_text(" ", strip=True)

    # status
    for status in ["Brand New", "Pre-owned", "Refurbished", "Open box", "Used", "New"]:
        if re.search(rf"\b{re.escape(status)}\b", all_text, re.I):
            item["status"] = status
            break

    # shipping
    shipping_text = None
    for r in rows:
        t = r.get_text(" ", strip=True)
        if re.search(r"shipping|delivery|postage", t, re.I):
            shipping_text = t
            break
    if shipping_text:
        if "free" in shipping_text.lower():
            item["shipping"] = 0
        else:
            item["shipping"] = parse_money_to_cents(shipping_text)

    # free returns
    if re.search(r"returns", all_text, re.I):
        item["free_returns"] = bool(re.search(r"free returns", all_text, re.I))

    # items sold
    item["items_sold"] = parse_items_sold(all_text)

    return item


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("search_term")
    parser.add_argument("--csv", action="store_true")
    args = parser.parse_args()

    session = requests.Session()
    session.headers.update(HEADERS)

    all_items = []
    for page in range(1, 11):
        print(f"Scraping page {page}...")
        try:
            html = fetch_page(session, args.search_term, page)
        except Exception as e:
            print(f"  Skipping page {page}: {e}")
            continue

        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select("li.s-card, li.s-item")
        print(f"  Found {len(cards)} cards")

        for card in cards:
            item = parse_card(card)
            if item["name"] is not None:
                all_items.append(item)

    filename_base = args.search_term.replace(" ", "_")

    if args.csv:
        filename = filename_base + ".csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["name", "price", "status", "shipping", "free_returns", "items_sold"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_items)
    else:
        filename = filename_base + ".json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(all_items, f, indent=2)

    print(f"Saved {len(all_items)} items to {filename}")


if __name__ == "__main__":
    main()
