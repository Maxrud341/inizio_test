import asyncio
import httpx
import re
import user_data

params = user_data.params
cookies = user_data.cookies
headers = user_data.headers

pattern = re.compile(r"^https://www\.idnes\.cz/.*/.*A\d{6}_\d{6}.*$")


async def fetch_archive_page(client: httpx.AsyncClient, page: int, start_page: int | None) -> str:
    if page == 1 and (start_page is None or start_page == 1):
        url = 'https://www.idnes.cz/zpravy/archiv/'
    else:
        url = f'https://www.idnes.cz/zpravy/archiv/{page}'
    resp = await client.get(url, params=params)
    resp.raise_for_status()
    return resp.text


async def get_idnes_news_links_async(maxlinks: int | None = None,
                                     maxpages: int | None = None,
                                     start_page: int | None = None) -> list[str]:
    if maxlinks is None and maxpages is None:
        raise ValueError("Нужно указать хотя бы maxlinks или maxpages.")
    if maxpages is None:
        num_pages = (maxlinks + 34) // 31
    else:
        num_pages = maxpages

    all_matching_links = set()
    start = 1 if start_page is None else start_page

    async with httpx.AsyncClient(headers=headers, cookies=cookies, timeout=30) as client:
        pages = range(start, start + num_pages)
        tasks = [fetch_archive_page(client, page, start_page) for page in pages]
        for coro in asyncio.as_completed(tasks):
            html = await coro
            links = re.findall(r'href="([^"]+)"', html)
            page_links = set(link for link in links if pattern.match(link))
            all_matching_links.update(page_links)
            stop_by_links = maxlinks is not None and len(all_matching_links) >= maxlinks
            print(f"Found {len(page_links)} links on a page, total collected: {len(all_matching_links)}")
            if stop_by_links:
                break

    if maxlinks is not None:
        return list(all_matching_links)[:maxlinks]
    else:
        return list(all_matching_links)


def run(maxlinks: int | None = None, maxpages: int | None = None, start_page: int | None = None) -> list[str]:
    return asyncio.run(get_idnes_news_links_async(maxlinks=maxlinks, maxpages=maxpages, start_page=start_page))
