import os, re, json, time, requests
from urllib.parse import urlparse

ESIK = 70        # yüzde 70 ve üzeri düşüşte bildirim
MAX_SAYFA = 8

# HTML ile taranan siteler: [kategori_linki, sayfa_parametresi]
KATEGORILER = [
    ["https://www.koton.com/erkek-tisort/", "page"],
    ["https://www.n11.com/telefon-ve-aksesuarlari", "pg"],
    ["https://www.n11.com/bilgisayar", "pg"],
    ["https://www.n11.com/bilgisayar/dizustu-bilgisayar", "pg"],
    ["https://www.tudors.com", "page"],
    ["https://tr.uspoloassn.com", "page"],
    # Yeni kategori eklemek icin: sitede URUNLERIN FIYATLARIYLA listelendigi
    # sayfaya kadar in, linki kopyala, buraya satir olarak ekle:
    # ["LINK", "pg"],   (N11 icin "pg", digerleri icin "page")
]

# Shopify altyapili siteler (koleksiyon linki)
SHOPIFY_KOLEKSIYONLAR = [
    "https://www.korendy.com.tr/collections/all",
    "https://www.wallartistanbul.com/collections/tum-islami-eserler",
    "https://www.kigili.com/collections/all",
    "https://www.dagi.com.tr/collections/all",
    "https://www.patirti.com/collections/all",
    "https://www.derimod.com.tr/collections/all",
]

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
BASLIK = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9",
}

def bildir(mesaj):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                  data={"chat_id": CHAT_ID, "text": mesaj})

def tl_virgul(m):
    return float(m.replace(".", "").replace(",", "."))

def sayfa_tara(url):
    p = urlparse(url)
    kok = f"{p.scheme}://{p.netloc}"
    ana_alan = ".".join(p.netloc.split(".")[-2:])
    r = requests.get(url, headers=BASLIK, timeout=30)
    html = r.text
    urunler = {}
    linkler = list(re.finditer(r'<a[^>]+href="(https?://[^"#? ]+|/[^"#? ]+)"', html))
    for i, m in enumerate(linkler):
        link = m.group(1)
        if link.startswith("/"):
            link = kok + link
        if ana_alan not in urlparse(link).netloc:
            continue
        son_parca = link.rstrip("/").split("/")[-1]
        urun_gibi = ("/products/" in link or "-p-" in link
                     or "urun." in urlparse(link).netloc
                     or re.search(r"\d{5,}", son_parca))
        if not urun_gibi:
            continue
        bas = m.end()
        son = linkler[i + 1].start() if i + 1 < len(linkler) else min(len(html), bas + 2500)
        blok = html[bas:son]
        fiyatlar = [tl_virgul(f) for f in re.findall(r'(\d{1,3}(?:\.\d{3})*,\d{2})\s*TL', blok)]
        fiyatlar +=
