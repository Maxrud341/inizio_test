import json_writer
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import idnes_links_parser
import idnes_article_parser 
import user_data
import os

MAX_NEWS = 10000
WORKERS = 8
BATCH_PAGES = 24 - 1

params = user_data.params
cookies = user_data.cookies
headers = user_data.headers

def process_links(links):
    idnes_article_parser.run(links, headers, cookies)
    return []

def load_last_page():
    if os.path.exists("page.txt"):
        try:
            with open("page.txt", "r", encoding="utf-8") as f:
                return int(f.read().strip())
        except:
            return 1
    return 1

def save_page(page):
    with open("page.txt", "w", encoding="utf-8") as f:
        f.write(str(page))

def main():
    start_time = time.time()
    start_page = load_last_page()
    remaining = MAX_NEWS

    while remaining > 0:
        try:
            print(f"Start on page {start_page}")
            links = idnes_links_parser.run(remaining, BATCH_PAGES, start_page)
        except Exception as e:
            print(f"Error fetching links for pages {start_page}-{start_page + BATCH_PAGES - 1}: {e}")
            break

        if not links:
            print(f"No links found on pages {start_page}-{start_page + BATCH_PAGES - 1}")
            break

        chunk_size = (len(links) + WORKERS - 1) // WORKERS
        chunks = [links[i:i + chunk_size] for i in range(0, len(links), chunk_size)]

        with ThreadPoolExecutor(max_workers=WORKERS) as executor:
            futures = [executor.submit(process_links, chunk) for chunk in chunks]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error processing chunk: {e}")

        processed_count = len(links)
        if processed_count > remaining:
            processed_count = remaining
        remaining -= processed_count

        end_page = start_page + BATCH_PAGES
        save_page(end_page)
        print(f"End on page {end_page}")

        start_page = end_page + 1

    end_time = time.time()
    print(f"All done! Total execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
