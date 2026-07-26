import re, json, requests

ADAYLAR = {
    "Vatan Bilgisayar": "https://www.vatanbilgisayar.com/notebook/",
    "Defacto": "https://www.defacto.com.tr/erkek-tisort",
    "Koton": "https://www.koton.com/erkek-tisort/",
    "Boyner": "https://www.boyner.com.tr/erkek-tisort-c-1010",
    "FLO": "https://www.flo.com.tr/erkek-spor-ayakkabi",
    "Trendyol": "https://www.trendyol.com/erkek-t-shirt-x-g2-c73",
    "LCW (kontrol)": "https://www.lcw.com/erkek-tisort-t-345",
}

BASLIK = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9",
}

for isim, url in ADAYLAR.items():
    try:
        r = requests.get(url, headers=BASLIK, timeout=30)
        fiyat_sayisi = len(re.findall(r'\d[\d.,]*\s*TL', r.text))
        print(f"{isim}: HTTP {r.status_code} | sayfada bulunan fiyat sayisi: {fiyat_sayisi}")
    except Exception as e:
        print(f"{isim}: HATA - {e}")

with open("fiyatlar.json", "w") as f:
    json.dump({}, f)
