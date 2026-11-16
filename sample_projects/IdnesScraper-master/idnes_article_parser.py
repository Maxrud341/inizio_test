import asyncio
import httpx
from bs4 import BeautifulSoup
import re
import json_writer


def run(links: list[str], headers: dict, cookies: dict):
    asyncio.run(process_links_async(links, headers, cookies))

# -------------------- Article parser --------------------
async def fetch_article(client: httpx.AsyncClient, url: str) -> str | None:
    """Fetch article HTML, без фильтрации cookie consent."""
    try:
        resp = await client.get(url, follow_redirects=True)
        resp.raise_for_status()
        return resp.text

    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e} for {url}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e} for {url}")
        return None


async def parse_idnes_article_async(url: str, client: httpx.AsyncClient) -> set | None:
    html = await fetch_article(client, url)
    if html is None:
        return None

    soup = BeautifulSoup(html, "html.parser")

    # Title
    title_tag = soup.find("h1", class_="arttit")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # Category from URL
    category = ""
    try:
        category = url.split("idnes.cz/")[1].split("/")[0]
    except IndexError:
        pass

    # Photo count
    photos_count = 0
    gallery_tag = soup.find("div", class_="more-gallery")
    if gallery_tag:
        count_tag = gallery_tag.find("b")
        if count_tag and count_tag.text.isdigit():
            photos_count = int(count_tag.text)

    # Publish date
    publish_date = ""
    date_tag = soup.find("span", class_="time-date")
    if date_tag and date_tag.has_attr("content"):
        publish_date = date_tag["content"]

    # Comments count
    comments_count = 0
    comments_tag = soup.find("a", class_="btndsc")
    if comments_tag:
        spans = comments_tag.find_all("span")
        if spans:
            last_span = spans[-1]
            match = re.search(r"\((\d+)", last_span.get_text())
            if match:
                comments_count = int(match.group(1))

    # Article content
    content = ""
    content_div = soup.find("div", id="art-text")
    if content_div:
        paragraphs = content_div.find_all("p")
        content = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

    return {
        ("url", url),
        ("title", title),
        ("category", category),
        ("photos_count", photos_count),
        ("publish_date", publish_date),
        ("comments_count", comments_count),
        ("content", content)
    }


# -------------------- Processing --------------------
async def process_links_async(links: list[str], headers: dict = None, cookies: dict = None):
    headers = headers or {"User-Agent": "Mozilla/5.0"}

    async with httpx.AsyncClient(http2=True, headers=headers, cookies=cookies) as client:
        tasks = [parse_idnes_article_async(url, client) for url in links]
        articles_data = await asyncio.gather(*tasks)


        for data, url in zip(articles_data, links):
            if data is None:
                continue
            json_writer.json_add(data)
            print(f"Processed: {url}")


def run(links: list[str], headers: dict = None, cookies: dict = None):
    """Wrapper to run async function synchronously."""
    asyncio.run(process_links_async(links, headers, cookies))


# -------------------- ThreadPool wrapper --------------------
def process_links(links: list[str], headers: dict, cookies: dict):
    run(links, headers, cookies)





