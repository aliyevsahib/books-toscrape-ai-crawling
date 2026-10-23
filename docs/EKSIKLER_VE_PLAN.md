# Assignment Eksik Analizi ve Tamamlama Planı

Kaynak: `AI Driven CrawlingIngestion.docx`, bölüm bölüm yeniden kontrol edildi (23.10.2026).
Durum: ✅ tamam · ⚠️ kısmen · ❌ eksik

---

## 1) Veri Çekme — ✅

| Madde | Durum | Kanıt |
|---|---|---|
| Sitedeki TÜM kitaplar | ✅ | 1000/1000, 50/50 liste sayfası, 0 başarısız URL |
| Kitap adı | ✅ | `baslik` (kısaltılmamış başlık, `h1`) |
| Fiyat | ✅ | `fiyat` |
| Puan (1-5 arası sayı) | ✅ | `puan` int 1-5 |
| Stok durumu | ✅ | `stok_durumu` + ekstra `stok_adedi` |
| Kategori | ✅ | detay sayfası breadcrumb, kategori sayfalarıyla 50/50 eşleşti |

## 2) Kaydetme — ⚠️ (küçük)

| Madde | Durum | Yapılacak |
|---|---|---|
| `kitaplar.csv` adıyla kaydet | ⚠️ | Dosya şu an `data/kitaplar.csv` konumunda. Teslim klasörünün köküne de bir kopyası konacak. |
| Fiyat sayısal (51.77) | ✅ | float64 |
| Puan sayısal (3) | ✅ | int 1-5 |

## 3) Analiz — ⚠️

| Madde | Durum | Yapılacak |
|---|---|---|
| En az 2 grafik | ✅ | 3 PNG var (`charts/`) |
| Kategori başına ortalama fiyat (top 10) | ✅ | PNG var |
| Puan dağılımı | ✅ | PNG var |
| "Puanı yüksek kitaplar daha mı pahalı?" metni | ⚠️ | Cevap sadece `ANALIZ.md` dosyasında. Notebook'a da yazılacak. |
| **Notebook (.ipynb) + Python grafik kütüphaneleri** | ❌ | `analiz.ipynb` hazırlanacak: veri yükleme, temizlik kontrolü, 3+ grafik (matplotlib + seaborn), korelasyon, yorum metni. Çalıştırılmış haliyle (çıktılar görünür) kaydedilecek. |
| "Default" kategorisi notu | ❌ | Notebook'a ve rapora bir cümle eklenecek. |

## 4) Teknik Kurallar — ⚠️ (kanıt eksik)

| Madde | Durum | Yapılacak |
|---|---|---|
| Sayfa açılmazsa çökmesin | ⚠️ | Kodda var (retry, `failed_urls`) ama kanıtı yok. `tests/test_hata_yonetimi.py` eklenecek: 404 sayfa, timeout, boş HTML, eksik alan senaryolarında programın çökmediği gösterilecek. |
| Alan boş gelirse çökmesin | ⚠️ | Aynı test dosyasında gösterilecek. |
| İstekler arası 0.5-1 sn bekleme | ✅ | `fetch()` içinde `random.uniform(0.5, 1.0)`; log'daki zaman damgaları kanıt (~21 dk / ~1100 istek). |
| Python (requests + BS4, pandas, matplotlib) | ✅ | |

## TESLİM EDİLECEKLER

| # | Madde | Durum | Yapılacak |
|---|---|---|---|
| 1 | Kod: GitHub linki veya .zip | ❌ | GitHub reposu (GitHub MCP ile, bonusa da sayılır) ve/veya `teslim.zip` |
| 1 | README'de nasıl çalıştırılacağı | ⚠️ | Var, ama notebook, testler ve teslim yapısı eklenecek |
| 2 | `kitaplar.csv` | ✅ | (köke kopya) |
| 3 | Grafikler (PNG veya notebook) | ⚠️ | PNG var, notebook eklenecek |
| 4 | Prompt Günlüğü (5-10 prompt) | ❌ | Şu an sadece şablon. Bu çalışmadaki gerçek promptlarla 8-10 kayıt yazılacak: ne üretti, çalıştı mı, nasıl düzeltildi. |
| 5 | Yansıma Raporu (yarım sayfa, 4 soru) | ❌ | Şu an boş. 4 soru gerçek deneyime göre cevaplanacak. |
| + | Bonus bölümü (hangi MCP/skill, nasıl kuruldu, ne kazandırdı) | ❌ | Rapora eklenecek, kurulum ekran görüntüsü veya config dosyası ile. |
| + | Skill/kural dosyasının kendisi | ⚠️ | `SKILL.md` yazıldı ama teslim yapısında görünür değil ve kullanımı belgelenmedi. |

## İPUÇLARI

| İpucu | Durum | Yapılacak |
|---|---|---|
| İlk kod tüm sayfaları çekiyor mu kontrol et | ✅ | `next` linki döngüsü, 50 sayfa doğrulandı. Prompt günlüğü ve rapora yazılacak. |
| Bazı bilgiler detay/kategori sayfasında | ✅ | Kategori breadcrumb'dan alındı. Rapora yazılacak. |
| Toplam sayıyı sitedekiyle karşılaştır | ✅ | 1000 == 1000. Rapora yazılacak. |
| AI'a hata mesajı + beklenen sonuç ver | ❌ | Prompt günlüğünde en az bir örnek gösterilecek (ör. `Â£` encoding veya Windows konsolunda Türkçe karakter hatası). |

## BONUS (+10) — ❌ (henüz puan getirecek şekilde yapılmadı)

| Madde | Durum | Yapılacak |
|---|---|---|
| Skill / kural dosyası | ⚠️ | `.claude/skills/polite-scraper/SKILL.md` var. Ek olarak `AGENTS.md` ve `.cursor/rules/scraping.mdc` (Cursor / Antigravity / Copilot için aynı kurallar) eklenecek. Rapora kurulum adımları yazılacak. |
| MCP kullanımı | ❌ | **Playwright MCP** bilgisayarında kurulu ama çalışmıyor: `'npx' is not recognized` hatası veriyor (Node.js yok). Node.js LTS kurulunca Playwright MCP ile canlı sitede rastgele 5 kitap CSV ile karşılaştırılacak ve ekran görüntüsü alınacak. **GitHub MCP** ile kod repoya yüklenecek. Kullandığımız dosya erişimi (cihaz klasörü MCP'si) de rapora yazılacak. |
| Rapora: hangi MCP/skill, nasıl kuruldu, ne kazandırdı | ❌ | Yansıma raporunun bonus bölümü |

---

## Uygulama sırası

1. `analiz.ipynb` oluştur, çalıştır, çıktılarla kaydet (matplotlib + seaborn)
2. `tests/test_hata_yonetimi.py` ekle ve çalıştır
3. `AGENTS.md` ve `.cursor/rules/scraping.mdc` ekle (skill ile aynı kurallar)
4. Prompt günlüğünü gerçek promptlarla doldur
5. Yansıma raporunu yaz (4 soru + bonus)
6. README'yi güncelle, `kitaplar.csv` dosyasını köke kopyala
7. MCP: Node.js kurulunca Playwright MCP ile canlı doğrulama + ekran görüntüsü
8. GitHub reposu (GitHub MCP) ve `teslim.zip`

**Senden gerekenler:**
- Node.js LTS kurulumu (https://nodejs.org). Playwright MCP'nin çalışması için gerekli. Sistem kurulumu olduğu için bunu senin yapman gerekiyor.
- GitHub reposu konusunda karar (karttan seçebilirsin).
