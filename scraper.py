"""books.toscrape.com crawler (Strateji C: A + B).

B (ana veri): 50 liste sayfası -> 1000 detay sayfası -> data/raw_books.jsonl
A (doğrulama): 50 kategori sayfası (+ sayfalama) -> data/category_counts.json

Kullanım:
    python scraper.py            # tam çalıştırma (checkpoint'ten devam eder)
    python scraper.py --limit 5  # hızlı deneme: sadece 5 kitap
"""

import argparse
import json
import logging
import random
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
DATA_DIR = Path("data")
LOG_DIR = Path("logs")
RAW_FILE = DATA_DIR / "raw_books.jsonl"
CATEGORY_FILE = DATA_DIR / "category_counts.json"
SITE_FILE = DATA_DIR / "site_info.json"
FAILED_FILE = DATA_DIR / "failed_urls.json"

MIN_DELAY, MAX_DELAY = 0.5, 1.0
TIMEOUT = 10
MAX_RETRIES = 3

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

log = logging.getLogger("scraper")


def setup_logging():
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_DIR / "scraper.log", encoding="utf-8"),
        ],
    )


def fetch(session, url):
    """Sayfayı indirir ve BeautifulSoup döner. Başarısızsa None (program çökmez)."""
    for attempt in range(1, MAX_RETRIES + 1):
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))  # siteyi yormamak için
        try:
            resp = session.get(url, timeout=TIMEOUT)
            if resp.status_code == 404:
                log.warning("404 bulunamadı: %s", url)
                return None
            resp.raise_for_status()
            # Site charset belirtmiyor; requests ISO-8859-1 varsayar ve "Â£" çıkar.
            resp.encoding = "utf-8"
            return BeautifulSoup(resp.text, "html.parser")
        except requests.RequestException as exc:
            wait = 2 ** (attempt - 1)
            log.warning("Hata (%d/%d) %s: %s -> %ds sonra tekrar", attempt, MAX_RETRIES, url, exc, wait)
            time.sleep(wait)
    log.error("Vazgeçildi: %s", url)
    return None


def safe_text(node):
    return node.get_text(strip=True) if node else None


def parse_total_results(soup):
    """Ana sayfadaki '1000 results' sayısı."""
    form = soup.select_one("form.form-horizontal")
    strong = form.find("strong") if form else None
    try:
        return int(strong.get_text(strip=True))
    except (AttributeError, ValueError):
        return None


def get_categories(soup):
    links = soup.select("div.side_categories ul li ul li a")
    return [(a.get_text(strip=True), urljoin(BASE_URL, a["href"])) for a in links]


def iter_pages(session, start_url, failed):
    """'next' linki olduğu sürece sayfaları gezer (sayfa sayısı hard-code değil)."""
    url = start_url
    while url:
        soup = fetch(session, url)
        if soup is None:
            failed.append(url)
            return
        yield url, soup
        nxt = soup.select_one("li.next > a")
        url = urljoin(url, nxt["href"]) if nxt else None


def parse_listing(soup, page_url):
    return [urljoin(page_url, a["href"]) for a in soup.select("article.product_pod h3 > a")]


def parse_book(soup, url):
    """Detay sayfasından tüm alanlar. Eksik alan None olur."""
    book = {"url": url}

    def field(name, func):
        try:
            book[name] = func()
        except Exception as exc:  # tek alan bozuksa diğerleri yine alınır
            book[name] = None
            log.warning("Alan boş/bozuk '%s' %s: %s", name, url, exc)

    main = soup.select_one("div.product_main")
    field("title", lambda: safe_text(main.find("h1")))
    field("price_raw", lambda: safe_text(main.select_one("p.price_color")))
    field("rating_raw", lambda: next(c for c in main.select_one("p.star-rating")["class"] if c in RATING_MAP))
    field("availability_raw", lambda: " ".join(main.select_one("p.availability").get_text().split()))
    field("category", lambda: safe_text(soup.select("ul.breadcrumb li")[2].find("a")))

    table = {safe_text(r.th): safe_text(r.td) for r in soup.select("table.table-striped tr")}
    book["upc"] = table.get("UPC")
    if not book["upc"]:
        log.warning("UPC yok: %s", url)
    return book


def load_done():
    done = {}
    if RAW_FILE.exists():
        with RAW_FILE.open(encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    done[rec["url"]] = rec
                except (json.JSONDecodeError, KeyError):
                    continue
    return done


def crawl_categories(session, categories, failed):
    """Strateji A: her kategoride kaç kitap var (çapraz doğrulama)."""
    counts = {}
    for i, (name, url) in enumerate(categories, 1):
        n = 0
        for page_url, soup in iter_pages(session, url, failed):
            n += len(parse_listing(soup, page_url))
        counts[name] = n
        log.info("[A %d/%d] %s: %d kitap", i, len(categories), name, n)
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="deneme için en fazla N kitap")
    parser.add_argument("--skip-categories", action="store_true", help="A doğrulamasını atla")
    args = parser.parse_args()

    setup_logging()
    DATA_DIR.mkdir(exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (ABB Tech Academy GenAI assignment; educational scraper)"
    failed = []

    home = fetch(session, BASE_URL)
    if home is None:
        log.error("Ana sayfa açılamadı, çıkılıyor.")
        return
    total = parse_total_results(home)
    categories = get_categories(home)
    log.info("Sitede yazan toplam: %s kitap, %d kategori", total, len(categories))

    # B1: liste sayfalarından detay URL'leri
    detail_urls, n_pages = [], 0
    for page_url, soup in iter_pages(session, urljoin(BASE_URL, "catalogue/page-1.html"), failed):
        n_pages += 1
        detail_urls.extend(parse_listing(soup, page_url))
        log.info("[B liste] sayfa %d: toplam %d URL", n_pages, len(detail_urls))
        if args.limit and len(detail_urls) >= args.limit:
            break
    detail_urls = list(dict.fromkeys(detail_urls))  # sırayı koruyarak tekilleştir
    if args.limit:
        detail_urls = detail_urls[: args.limit]

    # B2: detay sayfaları (checkpoint'ten devam)
    done = load_done()
    todo = [u for u in detail_urls if u not in done]
    log.info("Detay: %d URL, %d zaten var, %d çekilecek", len(detail_urls), len(detail_urls) - len(todo), len(todo))

    def scrape_details(urls):
        missed = []
        with RAW_FILE.open("a", encoding="utf-8") as f:
            for i, url in enumerate(urls, 1):
                soup = fetch(session, url)
                if soup is None:
                    missed.append(url)
                    continue
                f.write(json.dumps(parse_book(soup, url), ensure_ascii=False) + "\n")
                f.flush()
                if i % 50 == 0 or i == len(urls):
                    log.info("[B detay] %d/%d", i, len(urls))
        return missed

    missed = scrape_details(todo)
    if missed:
        log.info("%d başarısız detay sayfası tekrar deneniyor", len(missed))
        missed = scrape_details(missed)
    failed.extend(missed)

    # A: kategori sayıları
    if not args.skip_categories and not args.limit:
        counts = crawl_categories(session, categories, failed)
        CATEGORY_FILE.write_text(json.dumps(counts, ensure_ascii=False, indent=2), encoding="utf-8")

    SITE_FILE.write_text(
        json.dumps({"total_results": total, "n_categories": len(categories),
                    "n_listing_pages": n_pages, "n_detail_urls": len(detail_urls)}, indent=2),
        encoding="utf-8",
    )
    FAILED_FILE.write_text(json.dumps(failed, indent=2), encoding="utf-8")
    log.info("Bitti. Başarısız URL sayısı: %d", len(failed))


if __name__ == "__main__":
    main()
