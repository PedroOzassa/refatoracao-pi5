import json
import requests
from bs4 import BeautifulSoup
import datetime


def parse_site(url: str) -> list[dict]:

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg", "img","meta", "link", "header", "footer", "nav", "aside"]):
        tag.decompose()

    main = soup.find("main") or soup.find("article") or soup.body

    sections = []
    current_title = None
    current_content = []
    seen = set()

    for tag in main.find_all(["h1", "h2", "h3", "h4", "button", "p", "li"]):

        text = " ".join(tag.get_text(" ", strip=True).split())

        if not text or len(text.split()) < 3 or text in seen:
            continue

        if tag.name in ["h1", "h2", "h3", "h4", "button"]:
            if current_title and current_content:
                sections.append({
                    "title": current_title,
                    "content": " ".join(current_content),
                    "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tag": tag.name,
                    "source": url
                })
            current_title = text
            current_content = []
            seen.add(text)

        elif tag.name in ["p", "li"] and text != current_title:
            current_content.append(text)
            seen.add(text)

    if current_title and current_content:
        sections.append({
            "title": current_title,
            "content": " ".join(current_content),
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tag": tag.name,
            "source": url
        })

    return sections


if __name__ == "__main__":
    sections = parse_site("https://agibank.com.br/emprestimo")
    print(json.dumps(sections, ensure_ascii=False, indent=2))