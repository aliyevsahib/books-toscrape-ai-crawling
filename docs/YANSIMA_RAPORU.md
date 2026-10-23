# Yansıma Raporu

**AI aracı:** Claude (Claude uygulaması: proje thread'i, bilgisayarımdaki klasöre erişim, Remote Control). **Dil:** Python (önerilen dil).

**AI size en çok nerede yardımcı oldu?**
En çok keşif ve planlama aşamasında yardımcı oldu. Kod yazmadan önce site yapısını çıkardı: kategorinin liste sayfasında olmayıp sadece detay sayfasındaki breadcrumb'da bulunduğunu, başlıkların kısaltıldığını ve `requests` kütüphanesinin bu sitede fiyatı `Â£51.77` olarak getireceğini önceden söyledi. Bu sayede ipuçlarında anlatılan tuzakların hiçbirine düşmedik. Hata yönetimi (retry, checkpoint, alan bazlı `None`) ve doğrulama script'i de çok hızlı çıktı. 1000 istekli tam crawl ilk denemede 0 hatayla bitti.

**AI nerede yanıldı veya eksik kaldı?**
- Assignment'ın "teslim edilecekler" ve bonus kısmını ilk turda eksik bıraktı. Notebook, prompt günlüğü, yansıma raporu ve MCP kullanımı ben hatırlatana kadar yapılmadı.
- Kendi çalışma ortamının siteye erişimi olmadığını kodu yazdıktan sonra fark etti. Çözüm olarak kodu benim bilgisayarımda çalıştırdı.
- Test sırasında kütüphane sürümlerinden kaynaklanan iki hata çıktı: Spearman korelasyonu için `scipy` gerekiyordu ve matplotlib'in `boxplot(labels=)` parametresi kaldırılmıştı. Bunları sahte veriyle yaptığı testte kendisi yakaladı.
- Dosyayı önce yanlış klasörde aradı.

**Sonuçların doğru olduğundan nasıl emin oldunuz?**
`validate.py` ile 12 otomatik kontrol yaptık ve hepsi geçti. Kitap sayısı sitede yazan sayıyla aynı (1000 = 1000) ve 50 liste sayfasının hepsi gezildi. UPC'lerin 1000'i de tekil, başarısız URL ve boş değer yok. Fiyat float, puan 1-5 arası tamsayı. En önemlisi **çapraz doğrulama:** kategori sayfalarından ayrıca sayılan kitapların toplamı da 1000 çıktı ve 50 kategorinin hepsinde sayılar detay sayfalarından gelenlerle birebir eşleşti. Ayrıca bilinen bir kaydı ("A Light in the Attic" = £51.77, 3 yıldız, Poetry, 22 adet) kontrol ettik. Son olarak `validate.py` dosyasının seçtiği rastgele 5 kitap ve bu bilinen kayıt Playwright MCP ile canlı sitede açılıp CSV ile karşılaştırıldı: 6/6 kitapta fiyat, puan, stok adedi ve kategori birebir aynı (`docs/MCP_DOGRULAMA.md`). Hata yönetimini de 16 birim testle kanıtladık (404, timeout, boş sayfa, eksik alan).

**Bir dahaki sefere neyi farklı yapardınız?**
Başta AI'a teslim listesini de içeren bir kontrol listesi verirdim, böylece kod bittiğinde rapor ve günlük de bitmiş olurdu. Prompt günlüğünü çalışırken tutardım. Ortamın siteye erişimini ve MCP için gereken araçları (Node.js) en başta kontrol ederdim.

---

## Bonus: MCP ve Skill / kural dosyası

**Hangi MCP'yi / skill'i kullandınız?**
1. **Skill:** `.claude/skills/polite-scraper/SKILL.md`. Projeye özel 11 scraping kuralı içeriyor: 0.5-1 sn bekleme, timeout + retry, çökmeden loglama, UTF-8, `urljoin`, sayfalama, checkpoint, sayısal CSV ve sitedeki toplamla doğrulama. Aynı kurallar diğer AI araçları için `AGENTS.md` (Antigravity / Copilot / Codex) ve `.cursor/rules/scraping.mdc` (Cursor) dosyalarında da var. `CLAUDE.md` dosyası da AI'a bu skill'i kullanmasını söylüyor.
2. **Dosya sistemi MCP'si (Claude'un cihaz klasörü araçları):** AI, Word dosyasını bu araçlarla okudu, kodu ve dosyaları bilgisayarımdaki klasöre yazdı ve kopyaların doğru olduğunu checksum ile kontrol etti.
3. **Playwright MCP:** canlı sitede rastgele 5 kitabı (+ bilinen kaydı) CSV ile karşılaştırmak için. 6/6 eşleşti, ekran görüntüsü `docs/img/playwright_dogrulama.png`.
4. **GitHub erişimi (Claude'un GitHub entegrasyonu):** repo bağlantısı ve kodun yüklenmesi. Repo: https://github.com/aliyevsahib/books-toscrape-ai-crawling

**Nasıl kurdunuz?**
- Skill: proje kökünde `.claude/skills/polite-scraper/SKILL.md` dosyası (frontmatter'da `name` ve `description`). Claude Code bu klasördeki skill'leri otomatik tanıyor. Cursor için `.cursor/rules/*.mdc`, diğer araçlar için kökteki `AGENTS.md` yeterli.
- Klasör erişimi: Claude uygulamasında `E:\GenAI - ABB Tech Academy` klasörünü projeye bağlayıp izin verdim.
- Playwright MCP: Claude uygulamasında Playwright eklentisi kurulu. Eklenti `npx @playwright/mcp` ile çalıştığı için Node.js LTS kurdum (https://nodejs.org), `node -v` / `npx -v` ile kontrol ettim ve Claude uygulamasını yeniden başlattım. Bundan önce eklenti `'npx' is not recognized` hatasıyla bağlanamıyordu.
- GitHub: claude.ai hesabıma GitHub bağlıydı. GitHub'da boş bir public repo açtım, Claude repoyu oturuma ekleyip kodu yükledi.

**Size ne kazandırdı? Kullanmasaydınız ne farklı olurdu?**
Skill dosyası sayesinde bekleme, hata yönetimi ve encoding kurallarını her promptta tekrar yazmak zorunda kalmadım. AI'ın yazdığı her kod bu kurallara uygun çıktı ve testler de bu kurallara göre yazıldı. Klasör erişimi sayesinde dosyaları kopyala-yapıştır yapmadan doğrudan projeme yazdırabildim. Playwright MCP sayesinde "sonuçlar doğru mu?" sorusunu kendi kodumun çıktısına güvenmek yerine gerçek tarayıcıda, siteden bağımsız bir okuma ile kontrol edebildim. Elle 5 sayfa açıp karşılaştırmak yerine bunu tek adımda ve kanıtıyla yaptı. GitHub erişimi sayesinde de kodu yüklemek için ayrı bir git kurulumu ve kopyalama işi gerekmedi. Bunlar olmasaydı AI sadece kod önerirdi; dosyaları taşımak, çalıştırmak ve doğrulamak benim elle yapmam gereken ayrı adımlar olurdu.
