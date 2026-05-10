import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque


def crawl(start_url: str) -> set[str]:
    visited = set()
    queue = deque([start_url])
    domain = urlparse(start_url).netloc
    successful_urls = set()

    while queue:
        url = queue.popleft()

        if url in visited:
            continue

        visited.add(url)

        try:
            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                continue

            successful_urls.add(url)

            soup = BeautifulSoup(response.text, "html.parser")

            for link in soup.find_all("a", href=True):
                full_url = urljoin(url, link["href"])
                parsed = urlparse(full_url)

                if parsed.netloc == domain:
                    clean_url = parsed.scheme + "://" + parsed.netloc + parsed.path

                    if clean_url not in visited:
                        queue.append(clean_url)

        except Exception as e:
            print(f"Erro em {url}: {e}")

    return successful_urls


if __name__ == "__main__":
    urls = crawl("https://agibank.com.br/")
    for url in urls:
        print(url)