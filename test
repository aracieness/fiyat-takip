import re, requests

SITELER = [
    "https://www.colins.com.tr", "https://www.kigili.com", "https://www.sarar.com",
    "https://www.dagi.com.tr", "https://www.penti.com", "https://www.suwen.com.tr",
    "https://www.avva.com.tr", "https://www.jakamen.com", "https://www.hatemoglu.com",
    "https://www.kip.com.tr", "https://www.mudo.com.tr", "https://www.yargici.com",
    "https://www.ipekyol.com.tr", "https://www.twist.com.tr", "https://www.machka.com.tr",
    "https://www.vakko.com", "https://www.beymen.com", "https://www.tudors.com",
    "https://www.altinyildizclassics.com.tr", "https://www.dsdamat.com",
    "https://www.pierrecardin.com.tr", "https://tr.uspoloassn.com", "https://www.lufian.com",
    "https://www.modanisa.com", "https://www.sefamerve.com", "https://www.tozlu.com",
    "https://www.patirti.com", "https://www.lidyana.com",
    "https://www.hotic.com.tr", "https://www.derimod.com.tr", "https://www.greyder.com",
    "https://www.ayakkabidunyasi.com.tr", "https://www.superstep.com.tr",
    "https://www.instreet.com.tr", "https://www.sportive.com.tr", "https://www.korayspor.com",
    "https://www.barcin.com", "https://www.lescon.com.tr", "https://www.hummel.com.tr",
    "https://www.sevil.com.tr", "https://www.cosmetica.com.tr", "https://www.flormar.com.tr",
    "https://www.goldenrose.com.tr", "https://www.farmasi.com.tr",
    "https://www.dermoeczanem.com", "https://www.tshop.com.tr", "https://www.rossmann.com.tr",
    "https://www.eveshop.com.tr",
    "https://www.englishhome.com.tr", "https://www.madamecoco.com.tr",
    "https://www.bernardo.com.tr", "https://www.korkmaz.com.tr", "https://www.emsan.com.tr",
    "https://www.evidea.com", "https://www.vivense.com", "https://www.dogtas.com",
    "https://www.istikbal.com", "https://www.bellona.com.tr", "https://www.tepehome.com.tr",
    "https://www.chakra.com.tr", "https://www.ozdilek.com.tr", "https://www.porland.com.tr",
    "https://www.koctas.com.tr", "https://www.bauhaus.com.tr", "https://www.tekzen.com.tr",
    "https://www.dr.com.tr", "https://www.bkmkitap.com", "https://www.kitapsepeti.com",
    "https://www.halkkitabevi.com", "https://www.pandora.com.tr",
    "https://www.toyzzshop.com", "https://www.ebebek.com",
    "https://www.petlebi.com", "https://www.petzzshop.com",
    "https://www.incehesap.com", "https://www.itopya.com", "https://www.gamegaraj.com",
    "https://www.sinerji.gen.tr", "https://www.monsternotebook.com.tr",
    "https://www.casper.com.tr", "https://www.arcelik.com.tr", "https://www.vestel.com.tr",
    "https://www.beko.com.tr", "https://www.teknobiyotik.com", "https://www.mobilcadde.com",
    "https://www.sokmarket.com.tr", "https://www.carrefoursa.com",
    "https://www.saatvesaat.com.tr", "https://www.atasay.com", "https://www.altinbas.com",
    "https://www.atasun.com", "https://www.zuhalmuzik.com", "https://www.doremusic.com",
    "https://www.supplementler.com", "https://www.proteinocean.com",
    "https://www.lastikcim.com.tr", "https://www.pazarama.com",
]

BASLIK = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9",
}

for url in SITELER:
    alan = url.split("//")[1].replace("www.", "")
    try:
        r = requests.get(url, headers=BASLIK, timeout=12)
        h = r.text
        virgullu = len(re.findall(r'\d{1,3}(?:\.\d{3})*,\d{2}\s*TL', h))
        noktali = len(re.findall(r'>\s*\d{2,6}\.\d{2}\s*<', h))
        jsn = len(re.findall(r'"(?:price|salePrice|sellingPrice|amount)"\s*:\s*"?\d', h))
        shopify = " | SHOPIFY" if "cdn/shop" in h else ""
        print(f"{alan}: HTTP {r.status_code} | TL:{virgullu} nokta:{noktali} json:{jsn}{shopify}")
    except Exception as e:
        print(f"{alan}: HATA - {type(e).__name__}")
