import os, re, json, time, requests
from urllib.parse import urlparse

ESIK = 50          # yuzde kac dususte bildirim gelsin
MAX_SAYFA = 5      # HTML kaynaklarda kategori basina en fazla sayfa
SHOPIFY_MAX = 30   # Shopify kaynaklarda en fazla sayfa (sayfa basi 250 urun)

# HTML ile taranan kaynaklar: [link, sayfa_parametresi]
KATEGORILER = [
    ["https://www.koton.com/erkek-tisort/", "page"],
    ["https://www.n11.com/telefon-ve-aksesuarlari", "pg"],
    ["https://www.n11.com/bilgisayar", "pg"],
    ["https://www.n11.com/bilgisayar/dizustu-bilgisayar", "pg"],
    ["https://www.tudors.com", "page"],
    ["https://tr.uspoloassn.com", "page"],
    ["https://www.happinessistanbul.com", "page"],
    ["https://www.slazenger.com.tr", "page"],
    ["https://www.pasabahcemagazalari.com", "page"],
    ["https://www.modalife.com.tr", "page"],
    ["https://www.kahvedunyasi.com", "page"],
    ["https://www.lastikborsasi.com", "page"],
    ["https://www.hawkchair.com", "page"],
    ["https://www.issimohome.com", "page"],
    ["https://www.petburada.com", "page"],
    ["https://www.olalook.com.tr", "page"],
    ["https://www.dekorazi.com", "page"],
    ["https://www.ambalajstore.com", "page"],
    ["https://www.robolinkmarket.com", "page"],
    ["https://www.akvaryummarket.com", "page"],
    ["https://www.deripabuc.com", "page"],
    ["https://www.bebeji.com", "page"],
    ["https://www.kozvit.com", "page"],
    ["https://www.alfemo.com.tr", "page"],
    ["https://www.kumtel.com", "page"],
    ["https://www.nezih.com.tr", "page"],
    ["https://www.elektrikdeposu.com", "page"],
    ["https://www.velespit.com", "page"],
    ["https://www.vitaminler.com", "page"],
    ["https://www.petihtiyac.com", "page"],
    ["https://www.gurmenet.com", "page"],
    ["https://www.sanalmarketim.com", "page"],
    ["https://www.lactone.com.tr", "page"],
    ["https://www.takidukkani.com", "page"],
    ["https://www.amboss.com.tr", "page"],
    ["https://www.efor.com.tr", "page"],
    ["https://www.medikalcim.com", "page"],
    ["https://www.adoreoyuncak.com", "page"],
    ["https://www.avmarketi.com", "page"],
    ["https://www.buenoshoes.com.tr", "page"],
    ["https://www.bikestore.com.tr", "page"],
    ["https://www.evdemo.com.tr", "page"],
    ["https://www.shopsa.com.tr", "page"],
    ["https://www.arnica.com.tr", "page"],
    ["https://www.otoaksesuarci.com", "page"],
    ["https://www.evkur.com.tr", "page"],
    ["https://www.modoko.com.tr", "page"],
    ["https://www.gsstore.org", "page"],
    ["https://www.xdrive.com.tr", "page"],
    ["https://www.dericlub.com", "page"],
    ["https://www.chavin.com.tr", "page"],
]

# Shopify altyapili kaynaklar (koleksiyon linki)
SHOPIFY_KOLEKSIYONLAR = [
    "https://www.korendy.com.tr/collections/all",
    "https://www.wallartistanbul.com/collections/tum-islami-eserler",
    "https://www.kigili.com/collections/all",
    "https://www.dagi.com.tr/collections/all",
    "https://www.patirti.com/collections/all",
    "https://www.derimod.com.tr/collections/all",
    "https://www.gizia.com/collections/all",
    "https://www.silkandcashmere.com/collections/all",
    "https://www.thepurestsolutions.com/collections/all",
    "https://www.jumbo.com.tr/collections/all",
    "https://www.lav.com.tr/collections/all",
    "https://www.cottonbox.com.tr/collections/all",
    "https://www.storks.com.tr/collections/all",
    "https://www.sementa.com/collections/all",
    "https://www.wessi.com/collections/all",
    "https://www.marjin.com.tr/collections/all",
    "https://www.bagmori.com/collections/all",
    "https://www.newwell.com.tr/collections/all",
    "https://www.nascita.com.tr/collections/all",
    "https://www.cosmed.com.tr/collections/all",
    "https://www.bionnex.com/collections/all",
    "https://www.lorisparfum.com/collections/all",
    "https://www.reiskuyumculuk.com/collections/all",
    "https://www.rampage.com.tr/collections/all",
    "https://www.ecocotton.com.tr/collections/all",
    "https://www.cilek.com/collections/all",
    "https://www.nehir.com.tr/collections/all",
    "https://www.king.com.tr/collections/all",
    "https://www.civilim.com/collections/all",
    "https://www.welcomebaby.com.tr/collections/all",
    "https://www.petgross.com/collections/all",
    "https://www.petshoptr.com/collections/all",
    "https://www.bisan.com.tr/collections/all",
    "https://www.hobium.com/collections/all",
    "https://www.zuhre.com.tr/collections/all",
    "https://www.dogaltakil.com/collections/all",
    "https://www.balparmak.com.tr/collections/all",
]

# WooCommerce altyapili kaynaklar (site kok adresi)
WOO_SITELER = [
    "https://www.endustriyelmutfak.com",
]

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
BASLIK = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9",
}


def bildir(mesaj):
    try:
        requests.post(
            "https://api.telegram.org/bot" + TOKEN + "/sendMessage",
            data={"chat_id": CHAT_ID, "text": mesaj}, timeout=20,
        )
    except Exception:
        pass


def tl_virgul(m):
    return float(m.replace(".", "").replace(",", "."))


def fiyat_bul(blok):
    sonuc = []
    for f in re.findall(r'(\d{1,3}(?:\.\d{3})*,\d{2})\s*TL', blok):
        sonuc.append(tl_virgul(f))
    for f in re.findall(r'>\s*(\d{2,6}\.\d{2})\s*<', blok):
        sonuc.append(float(f))
    for f in re.findall(r'(\d{1,3}(?:,\d{3})*\.\d{2})\s*TL', blok):
        sonuc.append(float(f.replace(",", "")))
    for f in re.findall(r'"(?:price|salePrice|sellingPrice|discountedPrice|amount)"\s*:\s*"?(\d{2,6}(?:\.\d{1,2})?)"?', blok):
        sonuc.append(float(f))
    return [f for f in sonuc if 50 <= f <= 500000]


def sayfa_tara(url):
    p = urlparse(url)
    kok = p.scheme + "://" + p.netloc
    ana_alan = ".".join(p.netloc.split(".")[-2:])
    r = requests.get(url, headers=BASLIK, timeout=25)
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
        urun_gibi = (
            "/products/" in link
            or "-p-" in link
            or "urun." in urlparse(link).netloc
            or re.search(r"\d{5,}", son_parca)
        )
        if not urun_gibi:
            continue
        bas = m.end()
        if i + 1 < len(linkler):
            son = linkler[i + 1].start()
        else:
            son = min(len(html), bas + 2500)
        fiyatlar = fiyat_bul(html[bas:son])
        if fiyatlar:
            fiyat = min(fiyatlar)
            if link not in urunler or fiyat < urunler[link]:
                urunler[link] = fiyat
    return urunler


def shopify_tara(koleksiyon):
    p = urlparse(koleksiyon)
    kok = p.scheme + "://" + p.netloc
    urunler = {}
    for sayfa in range(1, SHOPIFY_MAX + 1):
        url = koleksiyon + "/products.json?limit=250&page=" + str(sayfa)
        try:
            r = requests.get(url, headers=BASLIK, timeout=25)
        except Exception:
            break
        if r.status_code != 200:
            break
        try:
            veriler = r.json().get("products", [])
        except Exception:
            break
        if not veriler:
            break
        for pr in veriler:
            fiyatlar = []
            for v in pr.get("variants", []):
                try:
                    fiyatlar.append(float(v["price"]))
                except (KeyError, ValueError, TypeError):
                    pass
            fiyatlar = [f for f in fiyatlar if f >= 20]
            if fiyatlar:
                urunler[kok + "/products/" + pr["handle"]] = min(fiyatlar)
        time.sleep(0.3)
    return urunler


def woo_tara(kok):
    urunler = {}
    for sayfa in range(1, 21):
        url = kok + "/wp-json/wc/store/products?per_page=100&page=" + str(sayfa)
        try:
            r = requests.get(url, headers=BASLIK, timeout=25)
        except Exception:
            break
        if r.status_code != 200:
            break
        try:
            veriler = r.json()
        except Exception:
            break
        if not isinstance(veriler, list) or not veriler:
            break
        for pr in veriler:
            try:
                kurus = pr["prices"]["price"]
                ondalik = int(pr["prices"].get("currency_minor_unit", 2))
                fiyat = float(kurus) / (10 ** ondalik)
            except Exception:
                continue
            if fiyat >= 20 and pr.get("permalink"):
                urunler[pr["permalink"]] = fiyat
        time.sleep(0.3)
    return urunler


try:
    with open("fiyatlar.json") as f:
        eski = json.load(f)
except Exception:
    eski = {}

dusus_sayisi = 0


def isle(bulunan):
    global dusus_sayisi
    for link, fiyat in bulunan.items():
        onceki = eski.get(link)
        if onceki and fiyat <= onceki * (1 - ESIK / 100.0):
            dusus_sayisi += 1
            if dusus_sayisi <= 20:
                mesaj = "%" + str(ESIK) + "+ DUSUS!\n"
                mesaj += "{:,.2f} TL -> {:,.2f} TL\n".format(onceki, fiyat)
                mesaj += link
                bildir(mesaj)
        eski[link] = fiyat


toplam = 0

for kategori, prm in KATEGORILER:
    gorulen = set()
    for sayfa in range(1, MAX_SAYFA + 1):
        if sayfa == 1:
            url = kategori
        elif "?" in kategori:
            url = kategori + "&" + prm + "=" + str(sayfa)
        else:
            url = kategori + "?" + prm + "=" + str(sayfa)
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
        time.sleep(0.5)
    print("HTML", kategori, "->", len(gorulen))

for koleksiyon in SHOPIFY_KOLEKSIYONLAR:
    try:
        bulunan = shopify_tara(koleksiyon)
    except Exception as e:
        print("HATA:", koleksiyon, type(e).__name__)
        continue
    isle(bulunan)
    toplam += len(bulunan)
    print("SHOPIFY", koleksiyon, "->", len(bulunan))

for kok in WOO_SITELER:
    try:
        bulunan = woo_tara(kok)
    except Exception as e:
        print("HATA:", kok, type(e).__name__)
        continue
    isle(bulunan)
    toplam += len(bulunan)
    print("WOO", kok, "->", len(bulunan))

print("TOPLAM TAKIP EDILEN URUN:", toplam)
print("BULUNAN DUSUS:", dusus_sayisi)
bildir("Tarama tamamlandi: " + str(toplam) + " urun kontrol edildi, "
       + str(dusus_sayisi) + " adet %" + str(ESIK) + "+ dusus bulundu.")

with open("fiyatlar.json", "w") as f:
    json.dump(eski, f, separators=(",", ":"))
