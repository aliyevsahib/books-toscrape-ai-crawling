# books.toscrape.com — AI Driven Crawling / Ingestion

https://books.toscrape.com sitesindeki 1000 kitabın adını, fiyatını, puanını, stok durumunu ve kategorisini çeker,
temizleyip `data/kitaplar.csv` dosyasına kaydeder ve basit bir analiz yapar.

## Kurulum

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    |  macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Çalıştırma

```bash
python scraper.py --limit 5   # (isteğe bağlı) 5 kitaplık hızlı deneme
python scraper.py             # tam crawling, ~15-20 dk (istekler arası 0.5-1 sn bekleme)
python clean.py               # data/raw_books.jsonl -> data/kitaplar.csv
python validate.py            # doğrulama kontrolleri
python analyze.py             # charts/*.png + ANALIZ.md (script versiyonu)
jupyter notebook analiz.ipynb # analiz notebook'u (pandas + matplotlib + seaborn)
python -m pytest -v tests/    # hata yönetimi testleri (siteye istek atmaz)
```

Not: `analiz.ipynb` kökteki `kitaplar.csv` dosyasını okur. Bu dosya `clean.py` çıktısının (`data/kitaplar.csv`) teslim kopyasıdır.

`scraper.py` yarıda kesilirse tekrar çalıştırın, zaten çekilmiş kitapları atlar (checkpoint: `data/raw_books.jsonl`).
Deneme çalıştırmasından sonra tam çalıştırma öncesi `data/raw_books.jsonl` dosyasını silmeye gerek yok.

## Strateji (A + B, çapraz doğrulama)

- **B (ana veri):** 50 liste sayfası (`next` linki bitene kadar) → 1000 detay sayfası. Kategori detay sayfasındaki breadcrumb'dan alınır, çünkü liste sayfasında yoktur.
- **A (doğrulama):** 50 kategori sayfası ve onların kendi sayfaları gezilir, kategori başına kitap sayısı `data/category_counts.json` dosyasına yazılır. `validate.py` iki kaynağı karşılaştırır.

## Hata yönetimi ve etik

- Her istekten önce 0.5-1 sn rastgele bekleme, `timeout=10`, 3 deneme (1, 2, 4 sn backoff), 404'te deneme yok.
- Açılamayan sayfa loglanır ve `data/failed_urls.json` dosyasına yazılır; program çökmez. Sonda başarısız detay sayfaları bir kez daha denenir.
- Boş/bozuk alan `None` olur ve uyarı loglanır. Log: `logs/scraper.log`.
- Site charset göndermediği için `resp.encoding = "utf-8"` ayarlanır (yoksa fiyat `Â£51.77` gelir).

## `kitaplar.csv` kolonları

| Kolon | Tip | Örnek |
|---|---|---|
| baslik | str | A Light in the Attic |
| fiyat | float | 51.77 |
| puan | int (1-5) | 3 |
| stok_durumu | str | In stock |
| stok_adedi | int | 22 |
| kategori | str | Poetry |
| upc | str | a897fe39b1053632 |
| url | str | https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html |

## Teslim edilenler

| Assignment maddesi | Dosya |
|---|---|
| 1) Kod + README | `scraper.py`, `clean.py`, `validate.py`, `analyze.py`, `tests/`, bu README |
| 2) `kitaplar.csv` | `kitaplar.csv` (kök) |
| 3) Grafikler | `analiz.ipynb` (çalıştırılmış) + `charts/*.png` + `ANALIZ.md` |
| 4) Prompt günlüğü | `docs/PROMPT_GUNLUGU.md` |
| 5) Yansıma raporu | `docs/YANSIMA_RAPORU.md` |
| Bonus: skill / kural dosyası | `.claude/skills/polite-scraper/SKILL.md`, `AGENTS.md`, `.cursor/rules/scraping.mdc`, `CLAUDE.md` |
| Plan | `docs/CRAWLING_PLANI.md`, `docs/EKSIKLER_VE_PLAN.md` |
