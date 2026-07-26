import os, re, json, time, requests

ESIK = 80        # yüzde kaç düşüşte bildirim gelsin
MAX_SAYFA = 20   # kategori başına en fazla kaç sayfa taransın (sayfa başına ~100 ürün)

KATEGORILER = [
    "https://www.lcw.com/erkek-tisort-t-345",
    # Başka LCW kategorisi eklemek için: lcw.com'da kategoriye gir,
    # adres çubuğundaki linki kopyala, buraya tırnak içinde ve sonuna virgül koyarak yapıştır. Örnek:
    # "https://www.lcw.com/erkek-jean-t-194",
    # "https://www.lcw.com/outlet/kadin-giyim-t-10",
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

def tl(metin):
    return float(metin.replace(".", "").replace(",", "."))

def sayfa_tara(url):
    """Sayfadaki {urun_linki: fiyat} sözlüğünü döndürür."""
    r = requests.get(url, headers=BASLIK, timeout=30)
    html = r.text
    urunler = {}
    # LCW ürün linkleri "-o-" ve ürün numarası içerir
    linkler = list(re.finditer(r'href="((?:https?://www\.lcw\.com)?/[^"]*-o-\d+[^"]*)"', html))
    for i, m in enumerate(linkler):
        link = m.group(1)
        if link.startswith("/"):
            link = "https://www.lcw.com" + link
        bas = m.end()
        son = linkler[i + 1].start() if i + 1 < len(linkler) else min(len(html), bas + 3000)
        blok = html[bas:son]
        fiyatlar = [tl(f) for f in re.findall(r'(\d{1,3}(?:\.\d{3})*,\d{2})\s*TL', blok)]
        fiyatlar = [f for f in fiyatlar if f >= 50]
        if fiyatlar:
            fiyat = min(fiyatlar)  # indirimli fiyatı al
            if link not in urunler or fiyat < urunler[link]:
                urunler[link] = fiyat
    if not urunler:
        print("UYARI: urun bulunamadi:", url)
        print("HTTP durum kodu:", r.status_code)
        print("Sayfanin ilk 500 karakteri:")
        print(html[:500])
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
                bildir(f"🔥 %{ESIK}+ DUSUS!\n{onceki:,.2f} TL -> {fiyat:,.2f} TL\n{link}")
            eski[link] = fiyat
        toplam += len(bulunan)
        time.sleep(1)

print("Taranan urun-fiyat kaydi:", toplam)
with open("fiyatlar.json", "w") as f:
    json.dump(eski, f, indent=2)
