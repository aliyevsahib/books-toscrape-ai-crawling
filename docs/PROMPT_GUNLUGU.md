# Prompt Günlüğü

AI aracı: **Claude** (Claude uygulamasında proje + thread, bilgisayarımdaki klasöre erişim ve Remote Control ile).
Aşağıdaki promptlar bu projede verdiğim gerçek promptlardır (kısaltılmış yerler `...` ile gösterildi).
Her biri için AI'ın ne ürettiği, çalışıp çalışmadığı ve nasıl düzeltildiği yazıldı.

---

### Prompt 1 — Assignment'ı okutup plan çıkartma
**Prompt:**
> "Sen uzman bir software engineersin ve web scraping, data crawling konularında oldukça deneyimli bir expertsin. Sana "E:\GenAI - ABB Tech Academy" folderini bu proje için çalışma alanı olarak veriyorum. ... "AI Driven CrawlingIngestion.docx" isimli bir Word file-ı var. ... Senden o dosyanın içerisini okuyup bu assignmenti yapman için bir plan oluşturmanı istiyorum. Bir araştırmaya çık ve gereken verileri toplamaya henüz başlamadan ... bir data crawling planı oluştur."

**AI ne üretti:** Word dosyasını okudu, siteyi inceledi (1000 kitap, 20'şer kitaplık 50 sayfa, 50 kategori, kategorinin sadece detay sayfasındaki breadcrumb'da olduğu, fiyatın `£51.77` ve puanın `star-rating Three` şeklinde geldiği) ve `CRAWLING_PLANI.md` dosyasını yazdı. Planda 3 strateji karşılaştırıldı (A: kategori sayfaları, B: liste + detay sayfaları, C: ikisi birlikte çapraz doğrulama), AI'ın ilk kodda sık yaptığı 7 hata (sadece ilk sayfa, `Â£` encoding, kısaltılmış başlık, göreli URL'ler, ...) ve bir doğrulama listesi vardı.

**Çalıştı mı:** Evet.
**Gözlem / düzeltme:** AI dosyayı önce klasörün kökünde aradı ve "dosya yok" hatası aldı. Klasörü listeleyip dosyanın `Gen AI Assignment` alt klasöründe olduğunu kendisi buldu. "Henüz veri çekme" talimatına uydu, plan aşamasında hiç crawling yapmadı.

---

### Prompt 2 — Strateji seçimi ve crawling'i başlatma
**Prompt:**
> "Planı güzel yazmışsın, hatalar, doğrulamalar ve projenin gereksinimlerine uygun bir yol çizmişsin. Crawling stratejisi olarak senin de söylediğin gibi "C. A + B birlikte (çapraz doğrulama)" iyi bir seçim. Data crawlinge başlayabilirsin."

**AI ne üretti:** `scraper.py` (bekleme, retry, checkpoint, A + B), `clean.py`, `validate.py`, `analyze.py`, README ve `polite-scraper` skill dosyası. Kodu önce sahte (test) veriyle denedi, sonra checksum ile doğrulayarak klasörüme kopyaladı.

**Çalıştı mı:** Kod ilk seferde çalıştı, ama ortam çalışmadı.
**Düzeltme:**
1. AI'ın kendi bulut ortamı `books.toscrape.com` adresine erişemedi (`CONNECT tunnel failed, response 403`). AI bunu hata mesajıyla birlikte bildirdi, siteyi taklit etmedi. Kodu bilgisayarımda çalıştırmak için Remote Control izni istedi.
2. Sahte veriyle yapılan testte iki hata yakaladı ve düzeltti: `Series.corr(method="spearman")` için `scipy` gerekiyordu (sıralama tabanlı Spearman ile çözüldü) ve matplotlib'in `boxplot(labels=...)` parametresi yeni sürümde kaldırılmıştı (`set_xticks` ile çözüldü).
3. Windows konsolunda Türkçe karakterler bozuk göründüğü için çalıştırırken `PYTHONIOENCODING=utf-8` ayarlandı. Bu sadece terminali etkiledi, dosyaları etkilemedi.

**Sonuç:** `--limit 5` deneme testi geçti (`£51.77`, `Â£` yok). Tam crawl ~21 dk sürdü: 1000/1000 kitap, 0 uyarı, 0 hata. `validate.py` 12/12 kontrolden geçti.

---

### Prompt 3 — İlerleme sorusu
**Prompt:**
> "Neden durdun? Şuanda görevini devam etmen için neye ihtiyacın var? Devam etmeni istiyorum."

**AI ne üretti:** Durmadığını, crawling'in bilgisayarımda devam ettiğini (o an 559/1000) ve 0.5-1 sn bekleme kuralı yüzünden ~1100 isteğin 15-20 dk süreceğini açıkladı.

**Çalıştı mı:** Evet.
**Ders:** Bekleme kuralı yüzünden uzun süren işlerde AI'dan ara ilerleme mesajı istemek, işin durduğu izlenimini ortadan kaldırıyor.

---

### Prompt 4 — Eksik analizi (gereksinimlere tek tek bakma)
**Prompt:**
> "Assignmentin tüm gereksinimleri henüz tam yapılmamış. "AI Driven CrawlingIngestion.docx" ... tekrar göz at. Görevlerde "1) Veri Çekme", "2) Kaydetme", "3) Analiz", "4) Teknik Kurallar" bunların her birinin açıklama kısımlarındaki tüm yazılanları yaptığından emin ol. Mesela "3) Analiz" kısmı için bir ipynb dosyası ve pythonun grafik oluşturma kütüphaneleri de kullanılarak görsel sonuçlar elde edilmesi istenmiş. "BONUS (+10 puan)" kısmı için MCP veya "Skill / kural dosyası" ... sen onu henüz yapmamışsın. ... Eksik kaldığın konuların her birini tek-tek bul ve onları yapmak ... için plan yap."

**AI ne üretti:** Docx'i madde madde tablo halinde kontrol eden `EKSIKLER_VE_PLAN.md` dosyası (✅ / ⚠️ / ❌). Ardından eksikleri sırayla tamamladı:
- `analiz.ipynb` (pandas + matplotlib + seaborn, çalıştırılmış ve çıktıları kayıtlı)
- `tests/test_hata_yonetimi.py`: 404, timeout, bağlantı hatası, 500, boş HTML, eksik alan, 0.5-1 sn bekleme. 16 test geçti.
- `AGENTS.md`, `.cursor/rules/scraping.mdc`, `CLAUDE.md` (skill ile aynı kurallar, farklı AI araçları için)
- bu prompt günlüğü ve yansıma raporu

**Çalıştı mı:** Evet.
**Ders:** AI ilk turda kodu ve veriyi çok iyi yaptı, ama "teslim edilecekler" ve bonus kısmını gözden kaçırdı. Gereksinimleri madde madde kontrol ettirmek bu açığı kapattı.

---

### Prompt 5 — Teslim şekli
**Prompt (karar kartı):** "Kodu GitHub'a mı yükleyelim, sadece zip mi olsun?" → **"Public GitHub repo + zip"** seçildi.

**AI ne üretti:** Hesabımdaki repoları listeledi ve bu proje için bir repo olmadığını gördü. Yeni repo oluşturma yetkisi olmadığını açıkça söyledi ve boş bir repo açmamı istedi.
**Çalıştı mı:** <repo açıldıktan sonra doldurulacak>

---

### Prompt 6 — Playwright MCP ile canlı doğrulama
**Prompt:** <doldurulacak>
**AI ne üretti:** <doldurulacak>
**Çalıştı mı:** <doldurulacak>
**Düzeltme:** İlk denemede Playwright MCP bilgisayarımda `'npx' is not recognized as an internal or external command` hatası verdi (Node.js kurulu değildi). <kurulum sonrası sonucu yaz>
