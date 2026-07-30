import re, requests

SITELER = [
    # --- Moda / giyim ---
    "https://www.oxxoshop.com",
    "https://www.adl.com.tr",
    "https://www.loft.com.tr",
    "https://www.network.com.tr",
    "https://www.gizia.com",
    "https://www.roman.com.tr",
    "https://www.nocturne.com.tr",
    "https://www.mizalle.com",
    "https://www.happinessistanbul.com",
    "https://www.silkandcashmere.com",
    "https://www.jimmykey.com",
    "https://www.bilcee.com",
    "https://www.slazenger.com.tr",
    "https://www.brandroom.com.tr",
    "https://www.morhipo.com",
    "https://www.setrms.com",
    "https://www.alvina.com.tr",
    "https://www.armine.com",
    "https://www.kayra.com.tr",
    "https://www.tugba.com.tr",
    "https://www.zulays.com",
    "https://www.tekbirgiyim.com",
    "https://www.panco.com.tr",
    "https://www.civil.com.tr",
    "https://www.joker.com.tr",
    # --- Ayakkabi / canta / deri ---
    "https://www.desa.com.tr",
    "https://www.divarese.com.tr",
    "https://www.inci.com.tr",
    "https://www.ninewest.com.tr",
    "https://www.matras.com.tr",
    "https://www.samsonite.com.tr",
    "https://www.kinetix.com.tr",
    "https://www.bambi.com.tr",
    # --- Kozmetik / kisisel bakim ---
    "https://www.thepurestsolutions.com",
    "https://www.narecza.com",
    "https://www.thebodyshop.com.tr",
    "https://www.yvesrocher.com.tr",
    "https://www.avon.com.tr",
    "https://www.oriflame.com.tr",
    "https://www.notecosmetics.com",
    "https://www.pastel.com.tr",
    "https://www.huncabeauty.com",
    "https://www.procsin.com",
    "https://www.mecitefendi.com",
    "https://www.eyup-sabri-tuncer.com",
    # --- Ev / mutfak / tekstil ---
    "https://www.jumbo.com.tr",
    "https://www.tchibo.com.tr",
    "https://www.schafer.com.tr",
    "https://www.lav.com.tr",
    "https://www.pasabahcemagazalari.com",
    "https://www.kutahyaporselen.com.tr",
    "https://www.karacahome.com",
    "https://www.cottonbox.com.tr",
    "https://www.linens.com.tr",
    "https://www.tac.com.tr",
    "https://www.yatasbedding.com.tr",
    "https://www.nurgaz.com.tr",
    "https://www.bella-maison.com",
    "https://www.mudo.com.tr/concept",
    # --- Mobilya ---
    "https://www.enzahome.com",
    "https://www.kelebek.com",
    "https://www.mondi.com.tr",
    "https://www.ikea.com.tr",
    "https://www.modalife.com.tr",
    "https://www.weltew.com",
    # --- Elektronik / teknoloji ---
    "https://www.turkcell.com.tr",
    "https://www.vodafone.com.tr",
    "https://www.philips.com.tr",
    "https://www.oyunfor.com",
    "https://www.gamesatis.com",
    "https://www.hizlial.com",
    "https://www.teknoinn.com",
    "https://www.pcdepo.com.tr",
    "https://www.gaming.gen.tr",
    "https://www.robotistan.com",
    # --- Kitap / kirtasiye / ofis ---
    "https://www.nadirkitap.com",
    "https://www.avansas.com",
    "https://www.ofix.com",
    "https://www.pttkitap.com",
    "https://www.remzi.com.tr",
    # --- Spor / outdoor ---
    "https://www.columbia.com.tr",
    "https://www.jackwolfskin.com.tr",
    "https://www.kampanya-outdoor.com",
    "https://www.bisikletgezgini.com",
    "https://www.fitnessmania.com.tr",
    # --- Gida / market / kahve ---
    "https://www.macrocenter.com.tr",
    "https://www.istegelsin.com",
    "https://www.tarimkredimarket.com.tr",
    "https://www.kahvedunyasi.com",
    "https://www.balparmak.com.tr",
    "https://www.elitcikolata.com",
    "https://www.tarispazar.com",
    "https://www.cikolatamarket.com",
    # --- Taki / saat / gozluk ---
    "https://www.goldstore.com.tr",
    "https://www.zenpirlanta.com",
    "https://www.storks.com.tr",
    "https://www.gozlukcum.com",
    # --- Evcil / oto / diger ---
    "https://www.patiliyo.com",
    "https://www.pethaus.com.tr",
    "https://www.otoyedekparcam.com",
    "https://www.lastikborsasi.com",
    "https://www.hobimo.com",
    "https://www.mobilyakeyfi.com",
]

BASLIK = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9",
}


def shopify_kapisi(kok):
    try:
        r = requests.get(kok + "/products.json?limit=250", headers=BASLIK, timeout=12)
        if r.status_code != 200:
            return " | SHOPIFY-KAPALI(" + str(r.status_code) + ")"
        adet = len(r.json().get("products", []))
        return " | SHOPIFY-ACIK(" + str(adet) + " urun/sayfa)"
    except Exception:
        return " | SHOPIFY-KAPALI(hata)"


print("=" * 70)
print("SITE TESTI - toplam", len(SITELER), "site")
print("=" * 70)

for url in SITELER:
    alan = url.split("//")[1].replace("www.", "")
    try:
        r = requests.get(url, headers=BASLIK, timeout=12)
        h = r.text
        virgullu = len(re.findall(r'\d{1,3}(?:\.\d{3})*,\d{2}\s*TL', h))
        noktali = len(re.findall(r'>\s*\d{2,6}\.\d{2}\s*<', h))
        jsn = len(re.findall(r'"(?:price|salePrice|sellingPrice|amount)"\s*:\s*"?\d', h))
        ek = ""
        if "cdn/shop" in h or "cdn.shopify" in h:
            ek = shopify_kapisi(url.rstrip("/"))
        print(alan + ": HTTP " + str(r.status_code)
              + " | TL:" + str(virgullu)
              + " nokta:" + str(noktali)
              + " json:" + str(jsn) + ek)
    except Exception as e:
        print(alan + ": HATA - " + type(e).__name__)

print("=" * 70)
print("BITTI")
