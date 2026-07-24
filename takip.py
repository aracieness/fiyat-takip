import os, re, json, time, requests

ESIK = 90        # yüzde kaç düşüşte bildirim gelsin
MAX_SAYFA = 10   # kategori başına en fazla kaç sayfa taransın

KATEGORILER = [
    "https://www.hepsiburada.com/laptop-notebook-dizustu-bilgisayarlar-c-98",
    # başka Hepsiburada kategorileri eklemek için: siteyi aç, kategoriye gir,
    # adres çubuğundaki linki kopyala ve buraya tırnak içinde, sonuna virgül koyarak yapıştır
]

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
BASLIK = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
}

def bildir(mesaj):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                  data={"chat_id": CHAT_ID, "text": mesaj})

def tl(metin):
    metin = metin.replace(".", "").replace(",", ".")
    return float(metin)

def sayfa_tara(url):
    """Sayfadaki {urun_linki: fiyat} sözlüğünü döndürür."""
    r = requests.get(url, headers=BASLIK, timeout=30)
    html = r.text
    urunler = {}
    # Hepsiburada ürün linkleri "-p-" kalıbı içerir
    linkler = list(re.finditer(r'"?(?:href|url)"?\s*[:=]\s*"((?:https?://www\.hepsiburada\.com)?/[^"]*-p-[A-Za-z0-9]+)[^"]*"', html))
    for i, m in enumerate(linkler):
        link = m.group(1)
        if link.startswith("/"):
            link = "https://www.hepsiburada.com" + link
        bas = m.end()
        son = linkler[i + 1].start() if i + 1 < len(linkler) else min(len(html), bas + 3000)
        blok = html[bas:son]
        fiyatlar = []
        # Örn: 12.345,67 TL biçimi
        fiyatlar += [tl(f) for f in re.findall(r'(\d{1,3}(?:\.\d{3})*,\d{2})\s*TL', blok)]
        # Örn: "price":12345.67 veya "amount":12345 biçimi (sayfa içi veri)
        fiyatlar += [float(f) for f in re.findall(r'"(?:price|amount|sellingPrice|discountedPrice)"\s*:\s*(\d+(?:\.\d+)?)', blok)]
        fiyatlar = [f for f in fiyatlar if f >= 100]
        if fiyatlar:
            fiyat = min(fiyatlar)
            if link not in urunler or fiyat < urunler[link]:
                urunler[link] = fiyat
    if not urunler:
        print("UYARI: urun bulunamadi:", url)
        print("HTTP durum kodu:", r.status_code)
        print("Bulunan link sayisi:", len(linkler))
        print("Sayfanin ilk 800 karakteri:")
        print(html[:800])
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
        url = kategori if sayfa == 1 else f"{kategori}?sayfa={sayfa}"
        bulunan = sayfa_tara(url)
        yeniler = set(bulunan) - gorulen
        if not yeniler:
            break
        gorulen |= yeniler
        for link, fiyat in bulunan.items():
            onceki = eski.get(link)
            if onceki and fiyat <= onceki * (1 - ESIK / 100):
                bildir(f"🔥 %{ESIK}+ DUSUS!\n{onceki:,.0f} TL -> {fiyat:,.0f} TL\n{link}")
            eski[link] = fiyat
        toplam += len(bulunan)
        time.sleep(3)

print("Taranan urun-fiyat kaydi:", toplam)
with open("fiyatlar.json", "w") as f:
    json.dump(eski, f, indent=2)
