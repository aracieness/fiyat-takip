import re, requests

ADAYLAR = {
    "Koton (kontrol)": "https://www.koton.com/erkek-tisort/",
    "Trendyol": "https://www.trendyol.com/cep-telefonu-x-c103498",
    "N11": "https://www.n11.com/bilgisayar/dizustu-bilgisayar",
    "Amazon TR": "https://www.amazon.com.tr/gp/bestsellers",
    "Teknosa": "https://www.teknosa.com/laptop-notebook-c-116004",
    "MediaMarkt": "https://www.mediamarkt.com.tr/tr/category/laptoplar-463.html",
    "Ciceksepeti": "https://www.ciceksepeti.com/cicek",
    "PTTAvm": "https://www.pttavm.com/elektronik",
    "Idefix": "https://www.idefix.com/kategori/kitap/",
    "Kitapyurdu": "https://www.kitapyurdu.com/index.php?route=product/best_seller",
    "Decathlon": "https://www.decathlon.com.tr/spor-ayakkabi",
    "FLO": "https://www.flo.com.tr/erkek-spor-ayakkabi",
    "Mavi": "https://www.mavi.com/erkek/c/2",
    "Beymen": "https://www.beymen.com/tr/kadin-10006",
    "Gratis": "https://www.gratis.com/makyaj-c-501",
    "Watsons": "https://www.watsons.com.tr/makyaj/c/2",
    "Karaca": "https://www.karaca.com/kahve-makineleri",
    "English Home": "https://www.englishhome.com/nevresim-takimlari",
    "Madame Coco": "https://www.madamecoco.com/sofra-mutfak",
    "Migros": "https://www.migros.com.tr/meyve-sebze-c-2",
    "A101": "https://www.a101.com.tr/kapida/elektronik",
}

BASLIK = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9",
}

for isim, url in ADAYLAR.items():
    try:
        r = requests.get(url, headers=BASLIK, timeout=25)
        h = r.text
        virgullu = len(re.findall(r'\d{1,3}(?:\.\d{3})*,\d{2}\s*TL', h))
        noktali = len(re.findall(r'>\s*\d{2,6}\.\d{2}\s*<', h))
        json_f = len(re.findall(r'"(?:price|salePrice|sellingPrice|amount)"\s*:\s*"?\d', h))
        print(f"{isim}: HTTP {r.status_code} | virgullu:{virgullu} noktali:{noktali} json:{json_f}")
    except Exception as e:
        print(f"{isim}: HATA - {type(e).__name__}")
