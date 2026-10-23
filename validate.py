"""kitaplar.csv için doğrulama kontrolleri (plan Bölüm 7)."""

import json
import sys
from pathlib import Path

import pandas as pd

df = pd.read_csv("data/kitaplar.csv")
site = json.loads(Path("data/site_info.json").read_text(encoding="utf-8"))
cat_file = Path("data/category_counts.json")
cat_counts = json.loads(cat_file.read_text(encoding="utf-8")) if cat_file.exists() else None
failed = json.loads(Path("data/failed_urls.json").read_text(encoding="utf-8"))

results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"[{'OK' if ok else 'FAIL'}] {name}" + (f"  ({detail})" if detail else ""))


expected = site["total_results"]
check("Toplam kitap == sitede yazan sayı", len(df) == expected, f"{len(df)} / {expected}")
check("Tüm liste sayfaları gezildi", site["n_listing_pages"] == 50, f"{site['n_listing_pages']} sayfa")
check("UPC'ler tekil", df["upc"].is_unique and df["upc"].notna().all(), f"{df['upc'].nunique()} tekil")
check("Başarısız URL yok", len(failed) == 0, f"{len(failed)} başarısız")
check("Hiç boş değer yok (zorunlu alanlar)",
      df[["baslik", "fiyat", "puan", "stok_durumu", "kategori"]].notna().all().all(),
      df.isna().sum().to_dict())
check("fiyat float", pd.api.types.is_float_dtype(df["fiyat"]), str(df["fiyat"].dtype))
check("puan tamsayı ve 1-5", pd.api.types.is_integer_dtype(df["puan"]) and df["puan"].between(1, 5).all(),
      str(sorted(df["puan"].unique())))
check("Fiyat aralığı makul", df["fiyat"].between(1, 100).all(),
      f"{df['fiyat'].min()} - {df['fiyat'].max()}")
check("Kategori sayısı == sitedeki", df["kategori"].nunique() == site["n_categories"],
      f"{df['kategori'].nunique()} / {site['n_categories']}")

if cat_counts is not None:
    detail_counts = df["kategori"].value_counts().to_dict()
    mismatches = {k: (v, detail_counts.get(k, 0)) for k, v in cat_counts.items() if v != detail_counts.get(k, 0)}
    check("A (kategori sayfaları) toplamı == 1000", sum(cat_counts.values()) == expected, f"{sum(cat_counts.values())}")
    check("A ve B kategori dağılımları birebir aynı", not mismatches, f"farklar: {mismatches}" if mismatches else "50/50 eşleşti")

known = df[df["baslik"] == "A Light in the Attic"]
ok = (len(known) == 1 and known.iloc[0]["fiyat"] == 51.77 and known.iloc[0]["puan"] == 3
      and known.iloc[0]["kategori"] == "Poetry" and known.iloc[0]["stok_adedi"] == 22)
check("Bilinen kayıt: A Light in the Attic = 51.77, 3, Poetry, 22", ok)

print("\nÖrnek 5 kitap (elle kontrol için):")
print(df.sample(5, random_state=42)[["baslik", "fiyat", "puan", "stok_adedi", "kategori", "url"]].to_string(index=False))

print(f"\nSONUÇ: {sum(results)}/{len(results)} kontrol geçti")
sys.exit(0 if all(results) else 1)
