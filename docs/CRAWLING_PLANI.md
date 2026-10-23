# AI Driven Crawling / Ingestion — Data Crawling Planı

**Hedef:** https://books.toscrape.com  ·  **Dil:** Python (requests + BeautifulSoup, pandas, matplotlib)
**Durum:** Sadece plan. Henüz veri çekilmedi.

---

## 1. Assignment gereksinimleri (kontrol listesi)

| # | Gereksinim | Puan | Planda karşılığı |
|---|---|---|---|
| 1 | TÜM kitaplar: ad, fiyat, puan (1-5), stok, kategori | 30 | Bölüm 3, 4 |
| 2 | `kitaplar.csv`, fiyat ve puan sayısal | 15 | Bölüm 5 |
| 3 | En az 2 grafik + "Puanı yüksek kitaplar daha mı pahalı?" metni | 15 | Bölüm 6 |
| 4 | Hata yönetimi + istekler arası 0.5-1 sn bekleme | 10 | Bölüm 4.3 |
| 5 | Prompt günlüğü (5-10 prompt) | 15 | Bölüm 8 |
| 6 | Yansıma raporu (yarım sayfa) | 15 | Bölüm 8 |
| + | Bonus: MCP / skill kullanımı | +10 | Bölüm 9 |

Teslim: kod (GitHub veya .zip) + README, `kitaplar.csv`, grafikler (PNG), prompt günlüğü, yansıma raporu, (varsa) skill/kural dosyası.

---

## 2. Site araştırması (keşif sonuçları)

Siteyi inceleyerek şunları doğruladım:

- Ana sayfada **"1000 results"** yazıyor. Doğrulama hedefimiz tam olarak **1000 kitap**.
- Sayfa başına **20 kitap**, toplam **50 sayfa** ("Page 1 of 50").
- Sayfalama: `catalogue/page-2.html` … `catalogue/page-50.html`. Son sayfada "next" linki yok.
- **50 kategori** var (Travel, Mystery, Historical Fiction, …). Kategori sayfaları da kendi içinde sayfalanıyor (ör. `.../mystery_3/page-2.html`).
- Liste sayfasındaki bir kitap kartı (`article.product_pod`):
  - Ad: `h3 > a` içindeki **`title` attribute'u** (görünen metin kısaltılmış: "A Light in the ...").
  - Fiyat: `p.price_color` → `£51.77`
  - Puan: `p.star-rating` class'ı → `star-rating Three` (kelime olarak)
  - Stok: `p.instock.availability` → sadece "In stock"
  - **Kategori liste sayfasında YOK** (ipucunda söylenen tuzak bu).
- Kitap detay sayfası (`catalogue/<slug>_<id>/index.html`):
  - Breadcrumb: Home > Books > **Poetry** > A Light in the Attic → kategori burada.
  - `h1` tam ad, fiyat, `star-rating` class'ı.
  - Availability: **"In stock (22 available)"** → stok adedi de çıkarılabilir.
  - Product Information tablosu: **UPC** (benzersiz kimlik), vergi, yorum sayısı.

### Bilinen tuzaklar (AI'ın ilk kodunda sık görülen hatalar)

1. **Sadece ilk sayfayı çekmek** → 20 kitap. Sayfalama döngüsü şart.
2. **Göreli URL'ler tutarsız:** ana sayfada linkler `catalogue/...`, catalogue sayfalarında `page-3.html`, detay linkleri `../../../...`. Çözüm: her zaman `urllib.parse.urljoin(current_url, href)`.
3. **Encoding hatası:** Site charset belirtmiyor, `requests` ISO-8859-1 varsayıyor ve fiyat `Â£51.77` geliyor. Çözüm: `response.encoding = "utf-8"` (veya `response.content` ile parse).
4. **Kısaltılmış başlık:** link metni değil `title` attribute kullanılmalı.
5. **Puan kelime olarak:** `{"One":1,"Two":2,"Three":3,"Four":4,"Five":5}` eşlemesi gerekir.
6. **Aynı isimli farklı kitaplar** olabilir → tekilleştirme başlığa göre değil, **UPC veya URL'ye göre** yapılmalı.
7. Kategoriler arasında "Default" ve "Add a comment" gibi anlamsız ama sitede gerçekten var olan kategoriler var. Bunları silmiyoruz, analizde not düşüyoruz.

---

## 3. Crawling stratejisi

Üç seçeneği karşılaştırdım:

| Strateji | İstek sayısı | Süre (~0.75 sn bekleme ile) | Artı | Eksi |
|---|---|---|---|---|
| A. Kategori sayfalarını gez | ~70 | ~1 dk | Hızlı, kategori bilgisi direkt | Stok adedi yok, UPC yok |
| B. 50 liste sayfası + 1000 detay sayfası | ~1050 | ~13-15 dk | Tüm alanlar tek, güvenilir kaynaktan; stok adedi + UPC | Daha yavaş |
| C. A + B birlikte (çapraz doğrulama) | ~1120 | ~15 dk | En güçlü doğrulama | En uzun |

**Önerim: B ana yöntem, A doğrulama için (yani C).**

- Ana veri: 50 liste sayfasından 1000 detay URL'si toplanır, her detay sayfasından tüm alanlar çekilir. Kategori breadcrumb'dan gelir.
- Doğrulama: 50 kategori sayfasındaki kitap sayıları toplanır ve detay sayfalarından gelen kategori dağılımıyla karşılaştırılır. Her ikisi de 1000 vermeli.

Bu, 30 puanlık "eksiksiz ve doğru" kriterini kanıtlanabilir hale getirir ve yansıma raporundaki "Sonuçların doğru olduğundan nasıl emin oldunuz?" sorusuna somut cevap verir.

### Akış

```
1. Ana sayfa → kategori listesi (50 ad + URL)                 [doğrulama için]
2. catalogue/page-1..50 → her sayfada 20 detay URL'si          ["next" linki bitene kadar]
3. 1000 detay sayfası → ad, fiyat, puan, stok, stok adedi, kategori, UPC, URL
4. Kategori sayfaları (+ kendi sayfalaması) → kategori başına kitap sayısı
5. Karşılaştır: toplam == 1000? kategori sayıları eşleşiyor mu? UPC tekil mi?
6. Temizle → kitaplar.csv
```

---

## 4. Teknik tasarım

### 4.1 Proje yapısı

```
books-scraper/
├── README.md                 # kurulum + çalıştırma
├── requirements.txt          # requests, beautifulsoup4, pandas, matplotlib, lxml
├── scraper.py                # crawling (adım 1-4)
├── clean.py                  # temizleme + kitaplar.csv (veya scraper içinde)
├── analyze.py                # grafikler + analiz metni
├── validate.py               # doğrulama kontrolleri (adım 5)
├── data/
│   ├── raw_books.jsonl       # ham veri (checkpoint)
│   └── kitaplar.csv          # TESLİM
├── charts/
│   ├── kategori_ortalama_fiyat_top10.png
│   ├── puan_dagilimi.png
│   └── puan_vs_fiyat.png     # ekstra (3. soru için)
├── logs/scraper.log
├── docs/
│   ├── PROMPT_GUNLUGU.md
│   └── YANSIMA_RAPORU.md
└── .claude/skills/polite-scraper/SKILL.md   # bonus (veya .cursor/rules)
```

### 4.2 Fonksiyonlar

- `fetch(url, session) -> BeautifulSoup | None` — tek giriş noktası; bekleme, retry, encoding, log burada.
- `get_categories(soup) -> list[(name, url)]`
- `iter_listing_pages(start_url)` — "next" linki olduğu sürece ilerler (sayfa sayısını hard-code etmez).
- `parse_listing(soup, base_url) -> list[detail_url]`
- `parse_book(soup, url) -> dict` — her alan ayrı `try/except` veya güvenli yardımcı (`safe_text`) ile; eksik alan `None` olur, program çökmez.
- `count_category(cat_url) -> int` — doğrulama için.

### 4.3 Hata yönetimi ve nezaket kuralları (10 puan)

- `requests.Session()` + anlamlı `User-Agent` başlığı.
- Her istekten önce `time.sleep(random.uniform(0.5, 1.0))`.
- `timeout=10` her istekte.
- Retry: 3 deneme, artan bekleme (1, 2, 4 sn). 404 gibi kalıcı hatalarda retry yok.
- Hata olursa: URL `failed_urls` listesine eklenir, loglanır, döngü devam eder. Sonda başarısız URL'ler bir kez daha denenir ve rapor edilir.
- Alan bazlı koruma: fiyat/puan/kategori bulunamazsa `None` yazılır ve uyarı loglanır.
- `logging` modülü: konsol + `logs/scraper.log`.
- Checkpoint: her kitap `raw_books.jsonl` dosyasına satır satır yazılır. Program yarıda kesilirse zaten çekilmiş URL'ler atlanır (yeniden 15 dk beklemeye gerek kalmaz).
- `robots.txt` kontrolü (site zaten scraping'e açık, ama yansıma raporunda etik nokta olarak bahsedilebilir).

---

## 5. Veri şeması ve temizleme (15 puan)

`kitaplar.csv` (UTF-8, virgülle ayrılmış, index yok):

| Kolon | Tip | Örnek | Kaynak / dönüşüm |
|---|---|---|---|
| `baslik` | str | A Light in the Attic | `h1` (strip) |
| `fiyat` | float | 51.77 | `£51.77` → regex `[\d.]+` → float |
| `puan` | int | 3 | `star-rating Three` → 3 |
| `stok_durumu` | str | In stock | Availability metninin ilk kısmı |
| `stok_adedi` | int | 22 | `(22 available)` → regex (ekstra alan) |
| `kategori` | str | Poetry | breadcrumb 3. eleman |
| `upc` | str | a897fe39b1053632 | Product Information tablosu (ekstra, tekillik için) |
| `url` | str | https://books.toscrape.com/catalogue/... | detay URL (ekstra) |

Zorunlu 5 alan + 3 ekstra alan. Ekstralar puan kaybettirmez ve doğrulamayı kolaylaştırır. İstenirse kolon adları İngilizce de olabilir (title, price, rating, availability, category). Önemli olan sayısal formatın doğru olması.

Temizleme kontrolleri:
- `fiyat` içinde `£` veya `Â` kalmadı mı? `dtype == float64`
- `puan` sadece {1,2,3,4,5} mi? `dtype == int64`
- Boş değer sayısı her kolon için 0 mı? (`df.isna().sum()`)
- `upc` tekrarı yok mu? (`df.upc.is_unique`)
- Satır sayısı == 1000

---

## 6. Analiz planı (15 puan)

1. **Grafik 1 — Kategori başına ortalama fiyat (en pahalı 10):** `groupby("kategori").fiyat.mean().nlargest(10)` → yatay bar grafiği, değer etiketleri, kategori başına kitap sayısını da etikette göster (az kitaplı kategorilerin ortalaması yanıltıcı olabilir, bunu not et).
2. **Grafik 2 — Puan dağılımı:** 1-5 puan için kitap sayısı, bar grafiği + yüzde etiketleri.
3. **Grafik 3 (ekstra) — Puan vs fiyat:** puana göre fiyat box plot'u (veya ortalama fiyat bar'ı).
4. **Metin cevabı — "Puanı yüksek kitaplar daha mı pahalı?":**
   - Puan bazında ortalama ve medyan fiyat tablosu.
   - Pearson / Spearman korelasyonu (`df.fiyat.corr(df.puan, method="spearman")`).
   - Beklenti: site verisi rastgele üretildiği için korelasyon sıfıra yakın çıkacak. Sonuç veriye göre yazılacak, önceden varsayılmayacak.

Grafikler `charts/` altına PNG (dpi=150) olarak kaydedilir. İstenirse aynısı bir Jupyter notebook'ta da gösterilir.

---

## 7. Doğrulama planı ("Sonuçlar doğru mu?")

- [ ] Toplam kitap sayısı == 1000 (sitede yazan sayı)
- [ ] 50 liste sayfasının hepsi ziyaret edildi (log'da 50 sayfa)
- [ ] UPC'ler tekil, 1000 adet
- [ ] 50 kategori sayısı ve kategori sayılarının toplamı == 1000 (A stratejisiyle çapraz kontrol)
- [ ] Rastgele 5 kitabı tarayıcıda açıp CSV ile elle karşılaştır (Playwright MCP ile de yapılabilir, bonus)
- [ ] Bilinen değerler: "A Light in the Attic" → 51.77, Poetry, 3 puan, In stock (22)
- [ ] Hiçbir sayısal kolonda NaN yok, fiyat aralığı makul (~10-60 £)

`validate.py` bu kontrolleri `assert` ile çalıştırır ve sonucu yazdırır. Çıktının ekran görüntüsü yansıma raporuna eklenebilir.

---

## 8. AI ile çalışma süreci (prompt günlüğü + yansıma = 30 puan)

Değerlendirmenin %30'u süreçle ilgili, bu yüzden çalışırken **kayıt tutmak** gerekiyor.

**Prompt günlüğü şablonu** (`docs/PROMPT_GUNLUGU.md`, her prompt için):

```
### Prompt N — <kısa başlık>
**Prompt:** <birebir metin>
**AI ne üretti:** <1-2 cümle>
**Çalıştı mı:** Evet / Kısmen / Hayır
**Düzeltme:** <hata mesajı + verdiğim yeni prompt>
```

Planlanan prompt sırası (gerçek akışta değişebilir, günlüğe gerçeği yazacağız):
1. Site yapısını inceletme (Playwright/Fetch MCP ile HTML seçicilerini çıkartma)
2. Tek sayfa scraper yazdırma
3. Sayfalama ekletme (ilk kod 20 kitap çekerse bu güzel bir "AI yanıldı" örneği)
4. Kategoriyi detay sayfasından aldırma
5. `Â£` encoding hatasını hata mesajıyla birlikte verip düzelttirme
6. Hata yönetimi + retry + bekleme ekletme
7. Temizleme ve CSV
8. Doğrulama script'i
9. Grafikler
10. README

İpucundaki kurala uyuyoruz: AI'a "çalışmıyor" yerine **hata mesajı + beklenen sonuç** veriyoruz.

**Yansıma raporu** (`docs/YANSIMA_RAPORU.md`, yarım sayfa): 4 soru + bonus bölümü. Çalışırken her "AI yanıldı" anını not edin, rapor kendiliğinden çıkar.

---

## 9. Bonus (+10): MCP ve skill

İkisini birden kullanmayı öneriyorum:

1. **Playwright MCP (veya Fetch MCP):** Kod yazmadan önce siteyi AI'a incelettirmek (seçiciler, sayfalama, breadcrumb) ve sonunda rastgele kitapları canlı sitede doğrulamak.
2. **Skill / kural dosyası:** `.claude/skills/polite-scraper/SKILL.md` (Claude Code) veya `.cursor/rules/scraping.mdc` / Antigravity proje talimatı. İçerik örneği:
   - Her istek arasında 0.5-1 sn bekle, timeout ve retry kullan.
   - Göreli URL'leri `urljoin` ile çöz, `response.encoding="utf-8"` ayarla.
   - Hataları logla, çökme; eksik alan `None` olsun.
   - Sonucu CSV'ye yaz, sayısal alanları dönüştür, toplamı sitedeki sayıyla doğrula.
3. **(İsteğe bağlı) GitHub MCP:** kodu repoya yüklemek.

Yansıma raporuna: hangi MCP/skill, nasıl kuruldu (config ekran görüntüsü), ne kazandırdı. Skill dosyası teslime eklenir.

---

## 10. Uygulama adımları ve tahmini süre

| Adım | İş | Süre |
|---|---|---|
| 1 | Ortam: venv, requirements, MCP + skill kurulumu | 20 dk |
| 2 | Site keşfi (MCP ile) | 10 dk |
| 3 | Scraper (liste + detay + hata yönetimi + checkpoint) | 45 dk |
| 4 | Tam çalıştırma (~1000 istek) | ~15 dk |
| 5 | Temizleme + `kitaplar.csv` + doğrulama | 20 dk |
| 6 | Analiz + grafikler + metin | 30 dk |
| 7 | README, prompt günlüğü, yansıma raporu | 40 dk |
| 8 | GitHub'a yükleme / zip | 10 dk |

Toplam: yaklaşık 3-3.5 saat.

---

## 11. Riskler

| Risk | Önlem |
|---|---|
| İlk kod tüm sayfaları çekmez | "next" linki döngüsü + 1000 kontrolü |
| Kategori eksik | Detay sayfası breadcrumb + kategori sayfası çapraz kontrol |
| `Â£` encoding | `response.encoding = "utf-8"` |
| Ağ hatası / yarıda kesilme | retry + checkpoint (jsonl) + başarısızları yeniden deneme |
| Aynı başlıklı kitaplar | UPC ile tekilleştirme |
| Az kitaplı kategoride yanıltıcı ortalama | Grafikte kitap sayısını göster, metinde not düş |
