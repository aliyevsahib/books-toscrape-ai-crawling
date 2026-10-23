"""Analiz: grafikler (charts/) + 'Puanı yüksek kitaplar daha mı pahalı?' metni."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

CHART_DIR = Path("charts")
CHART_DIR.mkdir(exist_ok=True)

df = pd.read_csv("data/kitaplar.csv")

# 1) Kategori başına ortalama fiyat - en pahalı 10
by_cat = df.groupby("kategori")["fiyat"].agg(["mean", "count"]).sort_values("mean", ascending=False)
top10 = by_cat.head(10).iloc[::-1]
fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.barh(top10.index, top10["mean"], color="#3b6ea5")
for bar, (mean, count) in zip(bars, top10[["mean", "count"]].values):
    ax.text(bar.get_width() + 0.4, bar.get_y() + bar.get_height() / 2,
            f"£{mean:.2f}  (n={int(count)})", va="center", fontsize=9)
ax.set_xlabel("Ortalama fiyat (£)")
ax.set_title("Kategori başına ortalama fiyat — en pahalı 10 kategori")
ax.set_xlim(0, top10["mean"].max() * 1.25)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(CHART_DIR / "kategori_ortalama_fiyat_top10.png", dpi=150)
plt.close(fig)

# 2) Puan dağılımı
dist = df["puan"].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(7, 4.5))
bars = ax.bar(dist.index.astype(str), dist.values, color="#3b6ea5")
for bar, v in zip(bars, dist.values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 3,
            f"{v}  (%{v / len(df) * 100:.1f})", ha="center", fontsize=9)
ax.set_xlabel("Puan (yıldız)")
ax.set_ylabel("Kitap sayısı")
ax.set_title(f"Kitapların puan dağılımı (n={len(df)})")
ax.set_ylim(0, dist.max() * 1.15)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(CHART_DIR / "puan_dagilimi.png", dpi=150)
plt.close(fig)

# 3) Puan vs fiyat
fig, ax = plt.subplots(figsize=(7, 4.5))
groups = [df.loc[df["puan"] == p, "fiyat"] for p in range(1, 6)]
ax.boxplot(groups, showmeans=True)
ax.set_xticks(range(1, 6), [str(p) for p in range(1, 6)])
ax.set_xlabel("Puan (yıldız)")
ax.set_ylabel("Fiyat (£)")
ax.set_title("Puana göre fiyat dağılımı")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(CHART_DIR / "puan_vs_fiyat.png", dpi=150)
plt.close(fig)

# Metin cevabı
by_rating = df.groupby("puan")["fiyat"].agg(["count", "mean", "median"]).round(2)
pearson = df["fiyat"].corr(df["puan"])
spearman = df["fiyat"].rank().corr(df["puan"].rank())  # Spearman (scipy gerektirmez)
diff = by_rating["mean"].max() - by_rating["mean"].min()

if abs(spearman) < 0.1:
    verdict = (f"Hayır. Puan ile fiyat arasında anlamlı bir ilişki yok (Spearman r = {spearman:.3f}, "
               f"Pearson r = {pearson:.3f}). Puan gruplarının ortalama fiyatları arasındaki en büyük fark "
               f"sadece £{diff:.2f}; yüksek puanlı kitaplar düşük puanlılardan belirgin şekilde pahalı değil.")
else:
    direction = "daha pahalı" if spearman > 0 else "daha ucuz"
    verdict = (f"Zayıf da olsa bir ilişki var: yüksek puanlı kitaplar ortalamada {direction} "
               f"(Spearman r = {spearman:.3f}, Pearson r = {pearson:.3f}, ortalamalar arası fark £{diff:.2f}).")

report = f"""# Analiz Sonuçları

## Kategori başına ortalama fiyat (en pahalı 10)

{by_cat.head(10).round(2).rename(columns={"mean": "ortalama_fiyat", "count": "kitap_sayisi"}).to_markdown()}

Not: Bazı kategorilerde çok az kitap var (n), bu kategorilerin ortalaması tek bir kitaba bağlı olabilir.

## Puan dağılımı

{dist.rename("kitap_sayisi").to_frame().to_markdown()}

## Puanı yüksek kitaplar daha mı pahalı?

{by_rating.rename(columns={"count": "kitap_sayisi", "mean": "ortalama", "median": "medyan"}).to_markdown()}

{verdict}

Grafikler: `charts/kategori_ortalama_fiyat_top10.png`, `charts/puan_dagilimi.png`, `charts/puan_vs_fiyat.png`
"""
Path("ANALIZ.md").write_text(report, encoding="utf-8")
print(report)
