import argparse
import requests
import json
from bs4 import BeautifulSoup

# --------------------------------------------------
# STEP 1: Get search term from command line
# --------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument('search_term')
parser.add_argument('--csv', action='store_true')  # extra credit flag
args = parser.parse_args()

# --------------------------------------------------
# STEP 2: Loop through 10 pages of eBay results
# --------------------------------------------------
search_query = args.search_term.replace(' ', '+')
all_items = []

for page in range(1, 11):
    print(f'Scraping page {page}...')
    url = f'https://www.ebay.com/sch/i.html?_nkw={search_query}&_pgn={page}'
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # --------------------------------------------------
    # STEP 3: Find all listings on the page
    # --------------------------------------------------
    listings = soup.select('.s-item')

    for listing in listings:
        item = {
            'name': None,
            'price': None,
            'status': None,
            'shipping': None,
            'free_returns': None,
            'items_sold': None,
        }

        # NAME
        name_tag = listing.select_one('.s-item__title')
        if name_tag:
            item['name'] = name_tag.text.strip()

        # PRICE (convert to cents, stored as int)
        price_tag = listing.select_one('.s-item__price')
        if price_tag:
            price_text = price_tag.text.strip()
            # Handle ranges like "$54.99 to $79.99" — just grab first number
            price_text = price_text.split(' ')[0]
            price_text = price_text.replace('$', '').replace(',', '')
            try:
                item['price'] = int(float(price_text) * 100)
            except:
                pass

        # STATUS (Brand New, Pre-owned, etc.)
        status_tag = listing.select_one('.SECONDARY_INFO')
        if status_tag:
            item['status'] = status_tag.text.strip()

        # SHIPPING
        ship_tag = listing.select_one('.s-item__shipping, .s-item__freeXDays')
        if ship_tag:
            ship_text = ship_tag.text.strip()
            if 'free' in ship_text.lower():
                item['shipping'] = 0
            else:
                ship_text = ship_text.replace('$', '').replace(',', '').split()[0]
                try:
                    item['shipping'] = int(float(ship_text) * 100)
                except:
                    pass

        # FREE RETURNS
        returns_tag = listing.select_one('.s-item__free-returns')
        item['free_returns'] = returns_tag is not None

        # ITEMS SOLD
        sold_tag = listing.select_one('.s-item__hotness, .s-item__additionalItemHotness')
        if sold_tag and 'sold' in sold_tag.text.lower():
            sold_text = sold_tag.text.strip().replace(',', '').split()[0]
            try:
                item['items_sold'] = int(sold_text)
            except:
                pass

        all_items.append(item)

print(f'Total items scraped: {len(all_items)}')

# --------------------------------------------------
# STEP 4: Save to JSON (or CSV for extra credit)
# --------------------------------------------------
filename_base = args.search_term.replace(' ', '_')

if args.csv:
    import csv
    filename = filename_base + '.csv'
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_items[0].keys())
        writer.writeheader()
        writer.writerows(all_items)
    print(f'Saved to {filename}')
else:
    filename = filename_base + '.json'
    with open(filename, 'w') as f:
        json.dump(all_items, f, indent=4)
    print(f'Saved to {filename}')
    