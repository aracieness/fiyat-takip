import os, re, json, time, requests
from urllib.parse import urlparse

ESIK = 80
MAX_SAYFA = 10

KATEGORILER = [
    "https://www.koton.com/erkek-tisort/",
    "https://www.boyner.com.tr/erkek-tisort-c-1010",
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

def tl_virgul(m):   # 1.299,99 bicimi
    return float(m.replace(".", "").replace(",", "."))

def sayfa_tara(url):
    kok = "{0.scheme}://{0.netloc}".format(urlparse(url))
    r = requests.get(url, headers=BASLIK, timeout=30)
    html = r.text
    urunler = {}
    linkler = list(re.finditer(r'<a[^>]+href="([^"#? ]+)"', html))
    for i, m in enumerate(linkler):
        link = m.group(1)
        if link.startswith("/"):
            link = kok + link
        if not link.startswith(kok):
            continue
        # sadece urun linkleri: son bolumde 5+ haneli sayi olmali
        son_parca = link.rstrip("/").split("/")[-1]
        if not re.search(r"\d{5,}", son_parca):
            continue
        bas = m.end()
        son = linkler[i + 1].start() if i + 1 < len(linkler) else min(len(html), bas + 2500)
        blok = html[bas:son]
        fiyatlar = [tl_virgul(f) for f in re.findall(r'(\d{1,3}(?:\.\d{3})*,\d{2})\s*TL', blok)]
        fiyatlar += [float(f) for f in re.findall(r'>\s*(\d{2,6}\.\d{2})\s*<', blok)]
        fiyatlar += [float(f) for f in re.findall(r'"(?:price|salePrice|amount|sellingPrice)"\s*:\s*"?(\d{2,6}(?:\.\d{1,2})?)"?', blok)]
        fiyatlar = [f for f in fiyatlar if 50 <= f <= 200000]
        if fiyatlar:
            fiyat = min(fiyatlar)
            if link not in urunler or fiyat < urunler[link]:
                urunler[link] = fiyat
    if not urunler:
        print("UYARI: urun bulunamadi:", url, "| HTTP:", r.status_code)
    return urunler

try:
    with open("fiyatlar.json") as f:
        eski = json.load(f)
except FileNotFoundError:
    eski = {}

toplam = 0
for kategori in KATEGORILER:
    gorulen = set()
    for sayfa in range(1, MAX_SAYFA + 1):
        url = kategori if sayfa == 1 else f"{kategori}{'&' if '?' in kategori else '?'}page={sayfa}"
        bulunan = sayfa_tara(url)
        yeniler = set(bulunan) - gorulen
        if not yeniler:
            break
        gorulen |= yeniler
        for link, fiyat in bulunan.items():
            onceki = eski.get(link)
            if onceki and fiyat <= onceki * (1 - ESIK / 100):
                bildir(f"🔥 %{ESIK}+ DUSUS!\n{onceki:,.2f} TL -> {fiyat:,.2f} TL\n{link}")
            eski[link] = fiyat
        toplam += len(bulunan)
        time.sleep(1)
    print(kategori, "-> takip edilen urun:", len(gorulen))

print("Taranan urun-fiyat kaydi:", toplam)
with open("fiyatlar.json", "w") as f:
    json.dump(eski, f, indent=2)
