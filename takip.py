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
    # Yeni N11 kategorisi eklemek için: n11.com'da kategorilere tıklaya tıklaya
    # ÜRÜNLERİN FİYATLARIYLA LİSTELENDİĞİ sayfaya kadar in, adres çubuğundaki
    # linki kopyala ve buraya yeni satır olarak ekle: ["LINK", "pg"],
    # Koton kategorisi için aynısı, sonu: "page"],
]
    # Yeni kategori eklemek için: siteye gir, kategoriyi aç, linki kopyala,
    # buraya yeni satır olarak ekle: ["LINK", "page"],  (N11 için "pg")
]

# Shopify altyapılı siteler
SHOPIFY_KOLEKSIYONLAR = [
    "https://www.korendy.com.tr/collections/all",
    "https://www.wallartistanbul.com/collections/tum-islami-eserler",
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
    ana_alan = ".".join(p.netloc.split(".")[-2:])   # n11.com, koton.com...
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
        fiyatlar += [float(f) for f in re.findall(r'>\s*(\d{2,6}\.\d{2})\s*<', blok)]
        fiyatlar += [float(f.replace(",", "")) for f in re.findall(r'(\d{1,3}(?:,\d{3})*\.\d{2})\s*TL', blok)]
        fiyatlar += [float(f) for f in re.findall(r'"(?:price|salePrice|sellingPrice|discountedPrice|amount)"\s*:\s*"?(\d{2,6}(?:\.\d{1,2})?)"?', blok)]
        fiyatlar = [f for f in fiyatlar if 50 <= f <= 500000]
        if fiyatlar:
            fiyat = min(fiyatlar)
            if link not in urunler or fiyat < urunler[link]:
                urunler[link] = fiyat
    if not urunler:
        print("UYARI: urun bulunamadi:", url, "| HTTP:", r.status_code)
    return urunler

def shopify_tara(koleksiyon):
    kok = "{0.scheme}://{0.netloc}".format(urlparse(koleksiyon))
    urunler = {}
    for sayfa in range(1, 30):
        url = f"{koleksiyon}/products.json?limit=250&page={sayfa}"
        r = requests.get(url, headers=BASLIK, timeout=30)
        if r.status_code != 200:
            print("UYARI: shopify erisilemedi:", url, "| HTTP:", r.status_code)
            break
        veriler = r.json().get("products", [])
        if not veriler:
            break
        for p in veriler:
            fiyatlar = []
            for v in p.get("variants", []):
                try:
                    fiyatlar.append(float(v["price"]))
                except (KeyError, ValueError, TypeError):
                    pass
            fiyatlar = [f for f in fiyatlar if f >= 20]
            if fiyatlar:
                urunler[kok + "/products/" + p["handle"]] = min(fiyatlar)
        time.sleep(1)
    return urunler

try:
    with open("fiyatlar.json") as f:
        eski = json.load(f)
except FileNotFoundError:
    eski = {}

def isle(bulunan):
    for link, fiyat in bulunan.items():
        onceki = eski.get(link)
        if onceki and fiyat <= onceki * (1 - ESIK / 100):
            bildir(f"🔥 %{ESIK}+ DUSUS!\n{onceki:,.2f} TL -> {fiyat:,.2f} TL\n{link}")
        eski[link] = fiyat

toplam = 0
for kategori, prm in KATEGORILER:
    gorulen = set()
    for sayfa in range(1, MAX_SAYFA + 1):
        url = kategori if sayfa == 1 else f"{kategori}{'&' if '?' in kategori else '?'}{prm}={sayfa}"
        try:
            bulunan = sayfa_tara(url)
        except Exception as e:
            print("HATA:", url, type(e).__name__)
            break
        yeniler = set(bulunan) - gorulen
        if not yeniler:
            break
        gorulen |= yeniler
        isle(bulunan)
        toplam += len(bulunan)
        time.sleep(1)
    print(kategori, "-> takip edilen urun:", len(gorulen))

for koleksiyon in SHOPIFY_KOLEKSIYONLAR:
    try:
        bulunan = shopify_tara(koleksiyon)
    except Exception as e:
        print("HATA:", koleksiyon, type(e).__name__)
        continue
    isle(bulunan)
    toplam += len(bulunan)
    print(koleksiyon, "-> takip edilen urun:", len(bulunan))

print("Taranan urun-fiyat kaydi:", toplam)
with open("fiyatlar.json", "w") as f:
    json.dump(eski, f, indent=2)
