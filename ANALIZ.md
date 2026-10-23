# Analiz Sonuçları

## Kategori başına ortalama fiyat (en pahalı 10)

| kategori         |   ortalama_fiyat |   kitap_sayisi |
|:-----------------|-----------------:|---------------:|
| Suspense         |            58.33 |              1 |
| Novels           |            54.81 |              1 |
| Politics         |            53.61 |              3 |
| Health           |            51.45 |              4 |
| New Adult        |            46.38 |              6 |
| Christian        |            42.5  |              3 |
| Sports and Games |            41.17 |              5 |
| Self Help        |            40.62 |              5 |
| Travel           |            39.79 |             11 |
| Fantasy          |            39.59 |             48 |

Not: Bazı kategorilerde çok az kitap var (n), bu kategorilerin ortalaması tek bir kitaba bağlı olabilir.

## Puan dağılımı

|   puan |   kitap_sayisi |
|-------:|---------------:|
|      1 |            226 |
|      2 |            196 |
|      3 |            203 |
|      4 |            179 |
|      5 |            196 |

## Puanı yüksek kitaplar daha mı pahalı?

|   puan |   kitap_sayisi |   ortalama |   medyan |
|-------:|---------------:|-----------:|---------:|
|      1 |            226 |      34.56 |    34.77 |
|      2 |            196 |      34.81 |    36.22 |
|      3 |            203 |      34.69 |    33.78 |
|      4 |            179 |      36.09 |    37.8  |
|      5 |            196 |      35.37 |    36.9  |

Hayır. Puan ile fiyat arasında anlamlı bir ilişki yok (Spearman r = 0.029, Pearson r = 0.028). Puan gruplarının ortalama fiyatları arasındaki en büyük fark sadece £1.53; yüksek puanlı kitaplar düşük puanlılardan belirgin şekilde pahalı değil.

Grafikler: `charts/kategori_ortalama_fiyat_top10.png`, `charts/puan_dagilimi.png`, `charts/puan_vs_fiyat.png`
