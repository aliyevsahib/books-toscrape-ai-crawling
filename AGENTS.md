# Proje talimatları (AI kodlama araçları için)

Bu dosya Antigravity, Copilot, Codex gibi `AGENTS.md` okuyan AI araçları içindir.
Aynı kurallar Claude Code için `.claude/skills/polite-scraper/SKILL.md`, Cursor için `.cursor/rules/scraping.mdc` dosyasında da var.

Proje: books.toscrape.com sitesinden 1000 kitabı çekip `kitaplar.csv` dosyasına yazan ve analiz eden bir Python projesi.
Dil: Python (requests + BeautifulSoup, pandas, matplotlib/seaborn). Testler: `python -m pytest tests/`.

# Polite scraper rules

When you write or edit scraping code in this project, always follow these rules:

1. **Bekleme:** Every HTTP request is preceded by `time.sleep(random.uniform(0.5, 1.0))`. Never send parallel requests.
2. **Timeout + retry:** Every request uses `timeout=10` and up to 3 retries with exponential backoff (1, 2, 4 s). Do not retry 404.
3. **Never crash:** A page that fails to load is logged and added to a `failed_urls` list; the loop continues. A missing field becomes `None` and is logged as a warning.
4. **Logging:** Use the `logging` module, to console and `logs/scraper.log`. No bare `print` for errors.
5. **Encoding:** books.toscrape.com sends no charset, so set `resp.encoding = "utf-8"` before parsing, otherwise prices become `Â£51.77`.
6. **URLs:** Resolve every `href` with `urljoin(current_page_url, href)`. Never build URLs by string concatenation.
7. **Pagination:** Follow `li.next > a` until it disappears. Never hard-code the page count.
8. **Full data:** Use the `title` attribute (not the truncated link text) and take the category from the detail page breadcrumb.
9. **Checkpoint:** Append each record to a `.jsonl` file as soon as it is scraped, and skip already scraped URLs on restart.
10. **Clean output:** Write `kitaplar.csv` with numeric `fiyat` (float, e.g. 51.77) and `puan` (int 1-5). Deduplicate by URL/UPC, not by title.
11. **Validate:** After scraping, compare the row count with the "N results" number on the home page and cross-check per-category counts from the category pages. Report any mismatch instead of hiding it.
