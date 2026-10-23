"""analiz.ipynb dosyasını üretir (kaynak hücreler burada, böylece notebook diff'lenebilir)."""

import nbformat as nbf

nb = nbf.v4.new_notebook()
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell

nb.cells = [
    md("""# books.toscrape.com — Veri Analizi

Bu notebook `scraper.py` ile çekilip `clean.py` ile temizlenen **`kitaplar.csv`** dosyasını analiz eder.

Cevaplanan sorular:
1. Kategori başına ortalama fiyat nedir? (en pahalı 10 kategori)
2. Kitapların puan dağılımı nasıldır?
3. Puanı yüksek kitaplar daha mı pahalı?

Kullanılan kütüphaneler: **pandas**, **matplotlib**, **seaborn**."""),
    code("""import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams["figure.dpi"] = 110
CHART_DIR = Path("charts")
CHART_DIR.mkdir(exist_ok=True)

df = pd.read_csv("kitaplar.csv")
print(df.shape)
df.head()"""),
    md("## 1. Veri kalitesi kontrolü\n\nAnalizden önce verinin eksiksiz ve sayısal alanların doğru tipte olduğunu kontrol ediyoruz."),
    code("""site = json.loads(Path("data/site_info.json").read_text(encoding="utf-8"))

print("Satır sayısı      :", len(df), "| sitede yazan:", site["total_results"])
print("Kategori sayısı   :", df["kategori"].nunique(), "| sitede:", site["n_categories"])
print("UPC tekil mi      :", df["upc"].is_unique)
print("fiyat tipi        :", df["fiyat"].dtype, "| aralık:", df["fiyat"].min(), "-", df["fiyat"].max())
print("puan tipi         :", df["puan"].dtype, "| değerler:", sorted(df["puan"].unique()))
print("\\nBoş değerler:")
print(df.isna().sum())"""),
    code("""df[["fiyat", "puan", "stok_adedi"]].describe().round(2)"""),
    md("## 2. Kategori başına ortalama fiyat (en pahalı 10 kategori)"),
    code("""by_cat = (df.groupby("kategori")["fiyat"]
            .agg(ortalama_fiyat="mean", kitap_sayisi="count")
            .sort_values("ortalama_fiyat", ascending=False))
top10 = by_cat.head(10)
top10.round(2)"""),
    code("""fig, ax = plt.subplots(figsize=(9, 5.5))
sns.barplot(data=top10.reset_index(), y="kategori", x="ortalama_fiyat", color="#3b6ea5", ax=ax)
for i, (mean, n) in enumerate(top10[["ortalama_fiyat", "kitap_sayisi"]].values):
    ax.text(mean + 0.5, i, f"£{mean:.2f}  (n={int(n)})", va="center", fontsize=9)
ax.set_xlim(0, top10["ortalama_fiyat"].max() * 1.25)
ax.set_xlabel("Ortalama fiyat (£)")
ax.set_ylabel("")
ax.set_title("Kategori başına ortalama fiyat — en pahalı 10 kategori")
fig.tight_layout()
fig.savefig(CHART_DIR / "kategori_ortalama_fiyat_top10.png", dpi=150)
plt.show()"""),
    md("""**Yorum:** Listenin başındaki kategorilerin çoğunda çok az kitap var (`n` değeri). Örneğin en üstteki kategorinin ortalaması tek bir kitabın fiyatı olabilir. Bu yüzden bu sıralama "o türün kitapları pahalıdır" şeklinde genellenmemeli. Daha güvenilir bir karşılaştırma için en az 10 kitabı olan kategorilere aşağıda ayrıca bakıyoruz.

Not: Sitede **"Default"** ve **"Add a comment"** adında, gerçek bir tür olmayan yer tutucu kategoriler var. Veri sitedeki haliyle bırakıldı, silinmedi."""),
    code("""by_cat[by_cat["kitap_sayisi"] >= 10].head(10).round(2)"""),
    md("## 3. Kitapların puan dağılımı"),
    code("""dist = df["puan"].value_counts().sort_index()
pd.DataFrame({"kitap_sayisi": dist, "yuzde": (dist / len(df) * 100).round(1)})"""),
    code("""fig, ax = plt.subplots(figsize=(7, 4.5))
sns.countplot(data=df, x="puan", color="#3b6ea5", ax=ax)
for p in ax.patches:
    h = p.get_height()
    ax.text(p.get_x() + p.get_width() / 2, h + 3, f"{int(h)}  (%{h / len(df) * 100:.1f})", ha="center", fontsize=9)
ax.set_ylim(0, dist.max() * 1.15)
ax.set_xlabel("Puan (yıldız)")
ax.set_ylabel("Kitap sayısı")
ax.set_title(f"Kitapların puan dağılımı (n={len(df)})")
fig.tight_layout()
fig.savefig(CHART_DIR / "puan_dagilimi.png", dpi=150)
plt.show()"""),
    md("**Yorum:** Puanlar 1-5 arasında oldukça dengeli dağılmış. En kalabalık grup 1 yıldız, en az kitap 4 yıldızda. Belirgin bir yüksek veya düşük puan yığılması yok."),
    md("## 4. Puanı yüksek kitaplar daha mı pahalı?"),
    code("""by_rating = df.groupby("puan")["fiyat"].agg(kitap_sayisi="count", ortalama="mean", medyan="median").round(2)
pearson = df["fiyat"].corr(df["puan"])
spearman = df["fiyat"].rank().corr(df["puan"].rank())
print(f"Pearson r  = {pearson:.3f}")
print(f"Spearman r = {spearman:.3f}")
print(f"Puan grupları arasındaki en büyük ortalama fark = £{by_rating['ortalama'].max() - by_rating['ortalama'].min():.2f}")
by_rating"""),
    code("""fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
sns.boxplot(data=df, x="puan", y="fiyat", color="#9cc0e7", showmeans=True, ax=axes[0])
axes[0].set_title("Puana göre fiyat dağılımı")
axes[0].set_xlabel("Puan (yıldız)")
axes[0].set_ylabel("Fiyat (£)")

sns.pointplot(data=df, x="puan", y="fiyat", errorbar=("ci", 95), color="#3b6ea5", ax=axes[1])
axes[1].set_title("Puana göre ortalama fiyat (%95 güven aralığı)")
axes[1].set_xlabel("Puan (yıldız)")
axes[1].set_ylabel("Ortalama fiyat (£)")
fig.tight_layout()
fig.savefig(CHART_DIR / "puan_vs_fiyat.png", dpi=150)
plt.show()"""),
    md("""### Cevap

**Hayır, puanı yüksek kitaplar belirgin şekilde daha pahalı değil.**

- Puan ile fiyat arasındaki korelasyon neredeyse sıfır (yukarıdaki Pearson ve Spearman değerleri ~0.03).
- 1 yıldızlı ve 5 yıldızlı kitapların ortalama fiyatları arasındaki fark sadece 1 £ civarında. Puan grupları arasındaki en büyük fark da yaklaşık 1.5 £.
- Kutu grafiklerinde beş puan grubunun fiyat aralıkları (yaklaşık 10-60 £) neredeyse birebir örtüşüyor. Ortalamaların güven aralıkları da birbirinin içine giriyor.

Bu sonuç şaşırtıcı değil, çünkü books.toscrape.com bir alıştırma sitesi ve fiyatlarla puanlar büyük ihtimalle birbirinden bağımsız, rastgele üretilmiş. Gerçek bir kitapçı verisinde aynı analiz farklı bir sonuç verebilir."""),
    md("## 5. Ek: stok durumu"),
    code("""print(df["stok_durumu"].value_counts())
df["stok_adedi"].describe().round(2)"""),
]

nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, "analiz.ipynb")
print("analiz.ipynb yazıldı")
