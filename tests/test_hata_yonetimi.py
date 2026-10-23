"""Hata yönetimi testleri: sayfa açılmazsa veya alan boş gelirse program çökmemeli.

Çalıştırma:  python -m pytest -v tests/
Siteye istek atılmaz; ağ hataları ve bozuk HTML taklit edilir (mock).
"""

import sys
from pathlib import Path
from unittest import mock

import pytest
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import clean  # noqa: E402
import scraper  # noqa: E402

FULL_BOOK = """
<ul class="breadcrumb"><li><a href="/">Home</a></li><li><a href="/b">Books</a></li>
<li><a href="/p">Poetry</a></li><li class="active">A Light in the Attic</li></ul>
<div class="product_main"><h1>A Light in the Attic</h1><p class="price_color">£51.77</p>
<p class="instock availability"> In stock (22 available) </p><p class="star-rating Three"></p></div>
<table class="table table-striped"><tr><th>UPC</th><td>a897fe39b1053632</td></tr></table>
"""


def response(status=200, text="<html></html>"):
    resp = mock.Mock(status_code=status, text=text)
    if status >= 400:
        resp.raise_for_status.side_effect = requests.HTTPError(f"{status} error")
    else:
        resp.raise_for_status.return_value = None
    return resp


@pytest.fixture(autouse=True)
def no_sleep():
    """Testlerde gerçek bekleme yapma, ama beklemenin çağrıldığını kaydet."""
    with mock.patch.object(scraper.time, "sleep") as sleep:
        yield sleep


def test_404_sayfa_none_doner_ve_tekrar_denemez():
    session = mock.Mock()
    session.get.return_value = response(404)
    assert scraper.fetch(session, "https://x/yok.html") is None
    assert session.get.call_count == 1


def test_baglanti_hatasi_3_kez_dener_sonra_none_doner():
    session = mock.Mock()
    session.get.side_effect = requests.ConnectionError("bağlantı koptu")
    assert scraper.fetch(session, "https://x/a.html") is None
    assert session.get.call_count == scraper.MAX_RETRIES


def test_timeout_sonrasi_basarili_olursa_sayfa_doner():
    session = mock.Mock()
    session.get.side_effect = [requests.Timeout("yavaş"), response(200, FULL_BOOK)]
    soup = scraper.fetch(session, "https://x/a.html")
    assert soup is not None and soup.h1.get_text() == "A Light in the Attic"


def test_500_hatasi_cokmez():
    session = mock.Mock()
    session.get.return_value = response(500)
    assert scraper.fetch(session, "https://x/a.html") is None


def test_her_istekten_once_0_5_1_sn_bekler(no_sleep):
    session = mock.Mock()
    session.get.return_value = response(200)
    for _ in range(20):
        scraper.fetch(session, "https://x/a.html")
    waits = [c.args[0] for c in no_sleep.call_args_list]
    assert len(waits) == 20
    assert all(0.5 <= w <= 1.0 for w in waits)


def test_iter_pages_acilmayan_sayfada_durur_ve_kaydeder():
    failed = []
    with mock.patch.object(scraper, "fetch", return_value=None):
        pages = list(scraper.iter_pages(mock.Mock(), "https://x/page-1.html", failed))
    assert pages == []
    assert failed == ["https://x/page-1.html"]


def test_tam_sayfa_dogru_ayrisir():
    book = scraper.parse_book(BeautifulSoup(FULL_BOOK, "html.parser"), "u")
    assert book == {
        "url": "u", "title": "A Light in the Attic", "price_raw": "£51.77", "rating_raw": "Three",
        "availability_raw": "In stock (22 available)", "category": "Poetry", "upc": "a897fe39b1053632",
    }


def test_bos_sayfa_cokmez_alanlar_none_olur():
    book = scraper.parse_book(BeautifulSoup("<html></html>", "html.parser"), "u")
    assert book["url"] == "u"
    assert all(book[k] is None for k in ["title", "price_raw", "rating_raw", "availability_raw", "category", "upc"])


def test_tek_alan_eksikse_digerleri_yine_alinir():
    html = FULL_BOOK.replace('<p class="price_color">£51.77</p>', "")
    book = scraper.parse_book(BeautifulSoup(html, "html.parser"), "u")
    assert book["price_raw"] is None
    assert book["title"] == "A Light in the Attic" and book["category"] == "Poetry"


@pytest.mark.parametrize("raw, expected", [("£51.77", 51.77), ("Â£51.77", 51.77), (None, None), ("", None)])
def test_fiyat_temizleme(raw, expected):
    assert clean.parse_price(raw) == expected


@pytest.mark.parametrize("raw, expected", [
    ("In stock (22 available)", ("In stock", 22)),
    ("In stock", ("In stock", 0)),
    (None, (None, None)),
])
def test_stok_temizleme(raw, expected):
    assert clean.parse_stock(raw) == expected
