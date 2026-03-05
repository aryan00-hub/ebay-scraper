import argparse
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Get search term from command line
parser = argparse.ArgumentParser()
parser.add_argument('search_term')
parser.add_argument('--csv', action='store_true')
args = parser.parse_args()

# Set up Chrome browser
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

search_query = args.search_term.replace(' ', '+')
all_items = []

for page in range(1, 11):
    print(f'Scraping page {page}...')
    url = f'https://www.ebay.com/sch/i.html?_nkw={search_query}&_pgn={page}'
    driver.get(url)
    time.sleep(4)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    cards = soup.select('.s-card')
    print(f'  Found {len(cards)} listings')

    for card in cards:
        item = {
            'name': None,
            'price': None,
            'status': None,
            'shipping': None,
            'free_returns': None,
            'items_sold': None,
        }

        # NAME
        name_tag = card.select_one('.s-card__title')
        if name_tag:
            item['name'] = name_tag.get_text(strip=True)

        # PRICE
        price_tag = card.select_one('.s-card__price')
        if price_tag:
            price_text = price_tag.get_text(strip=True).split(' ')[0]
            price_text = price_text.replace('$', '').replace(',', '')
            try:
                item['price'] = int(float(price_text) * 100)
            except:
                pass

        # CHECK ALL ATTRIBUTE ROWS for status, shipping, free returns, items sold
        rows = card.select('.s-card__attribute-row')
        for row in rows:
            text = row.get_text(strip=True)

            # STATUS
            if any(s in text for s in ['Brand New', 'Pre-owned', 'Refurbished', 'Open box']):
                item['status'] = text

            # SHIPPING
            if 'delivery' in text.lower() or 'shipping' in text.lower():
                if 'free' in text.lower():
                    item['shipping'] = 0
                else:
                    price_part = text.replace('$', '').replace(',', '').split()[0]
                    try:
                        item['shipping'] = int(float(price_part) * 100)
                    except:
                        pass

            # FREE RETURNS
            if 'return' in text.lower():
                item['free_returns'] = 'free' in text.lower()

            # ITEMS SOLD
            if 'sold' in text.lower():
                sold_text = text.lower().replace('sold', '').replace(',', '').strip()
                try:
                    item['items_sold'] = int(sold_text)
                except:
                    pass

        all_items.append(item)

driver.quit()
print(f'Total items scraped: {len(all_items)}')

# Save output
filename_base = args.search_term.replace(' ', '_')

if args.csv:
    import csv
    filename = filename_base + '.csv'
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_items[0].keys())
        writer.writeheader()
        writer.writerows(all_items)
else:
    filename = filename_base + '.json'
    with open(filename, 'w') as f:
        json.dump(all_items, f, indent=4)

print(f'Saved to {filename}')
