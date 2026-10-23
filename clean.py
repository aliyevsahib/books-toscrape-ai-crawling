"""data/raw_books.jsonl -> data/kitaplar.csv (sayısal alanlar temiz)."""

import re
from pathlib import Path

import pandas as pd

RAW_FILE = Path("data/raw_books.jsonl")
CSV_FILE = Path("data/kitaplar.csv")

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def parse_price(text):
    """'£51.77' (veya bozuk 'Â£51.77') -> 51.77"""
    if not isinstance(text, str):
        return None
    m = re.search(r"\d+(?:\.\d+)?", text)
    return float(m.group()) if m else None


def parse_stock(text):
    """'In stock (22 available)' -> ('In stock', 22)"""
    if not isinstance(text, str):
        return None, None
    status = text.split("(")[0].strip() or None
    m = re.search(r"\((\d+) available\)", text)
    return status, (int(m.group(1)) if m else 0)


def main():
    df = pd.read_json(RAW_FILE, lines=True)
    before = len(df)
    df = df.drop_duplicates(subset="url", keep="last")  # checkpoint tekrarlarına karşı

    stock = df["availability_raw"].apply(parse_stock)
    out = pd.DataFrame({
        "baslik": df["title"].str.strip(),
        "fiyat": df["price_raw"].apply(parse_price),
        "puan": df["rating_raw"].map(RATING_MAP).astype("Int64"),
        "stok_durumu": stock.str[0],
        "stok_adedi": stock.str[1].astype("Int64"),
        "kategori": df["category"].str.strip(),
        "upc": df["upc"],
        "url": df["url"],
    })

    out.to_csv(CSV_FILE, index=False, encoding="utf-8")
    print(f"{before} ham kayıt -> {len(out)} satır -> {CSV_FILE}")
    print("Boş değerler:\n" + out.isna().sum().to_string())


if __name__ == "__main__":
    main()
