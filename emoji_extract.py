import argparse
import csv
import json
import sys
import time

import requests
from bs4 import BeautifulSoup

URL = "https://unicode.org/emoji/charts/full-emoji-list.html"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; emoji-scraper/1.0; "
        "+https://github.com/example/emoji-scraper)"
    )
}


def fetch_page(url: str, timeout: int = 60) -> str:
    """Download the page with a generous timeout (it's ~10 MB)."""
    print(f"Fetching {url} …", flush=True)
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    print(f"  Downloaded {len(resp.content) / 1_048_576:.1f} MB", flush=True)
    return resp.text


def parse_emoji(html: str) -> list[dict]:
    """Parse the full-emoji-list table and return a list of emoji dicts."""
    print("Parsing HTML …", flush=True)
    soup = BeautifulSoup(html, "lxml")

    table = soup.find("table")
    if table is None:
        raise RuntimeError("Could not find the emoji table in the page.")

    rows = table.find_all("tr")
    print(f"  Found {len(rows):,} rows to process", flush=True)

    emojis = []
    current_group = ""
    current_subgroup = ""

    for row in rows:
        classes = row.get("class", [])

        # ── Group header ──────────────────────────────────────────────────
        if "bighead" in classes:
            a = row.find("a")
            current_group = a.get_text(strip=True) if a else row.get_text(strip=True)
            continue

        # ── Subgroup header ───────────────────────────────────────────────
        if "mediumhead" in classes:
            a = row.find("a")
            current_subgroup = a.get_text(strip=True) if a else row.get_text(strip=True)
            continue

        # ── Emoji data row ────────────────────────────────────────────────
        cols = row.find_all("td")
        if not cols:
            continue

        # Extract fields by class name for robustness
        def col_text(cls: str) -> str:
            td = row.find("td", class_=cls)
            return td.get_text(strip=True) if td else ""

        number_str = col_text("rchars")
        code = col_text("code")
        name = col_text("name")

        # The actual emoji character lives in <td class="chars">
        chars_td = row.find("td", class_="chars")
        char = chars_td.get_text(strip=True) if chars_td else ""

        # Skip rows that don't look like real emoji entries
        if not code or not name:
            continue

        try:
            number = int(number_str)
        except ValueError:
            number = None

        emojis.append(
            {
                "group": current_group,
                "subgroup": current_subgroup,
                "number": number,
                "code": code,
                "char": char,
                "name": name,
            }
        )

    print(f"  Parsed {len(emojis):,} emoji entries", flush=True)
    return emojis


def save_json(emojis: list[dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(emojis, f, ensure_ascii=False, indent=2)
    print(f"Saved JSON → {path}")


def save_csv(emojis: list[dict], path: str) -> None:
    if not emojis:
        print("No data to write.")
        return
    fields = list(emojis[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(emojis)
    print(f"Saved CSV  → {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape the Unicode full emoji list.")
    parser.add_argument(
        "--output", "-o",
        default="emoji.json",
        help="Output file path (default: emoji.json)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=60,
        help="HTTP request timeout in seconds (default: 60)",
    )
    args = parser.parse_args()

    t0 = time.perf_counter()

    html = fetch_page(URL, timeout=args.timeout)
    emojis = parse_emoji(html)

    if args.format == "csv":
        save_csv(emojis, args.output)
    else:
        save_json(emojis, args.output)

    elapsed = time.perf_counter() - t0
    print(f"Done in {elapsed:.1f}s")


if __name__ == "__main__":
    main()