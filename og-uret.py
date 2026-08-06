#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════
  OG SAYFA ÜRETİCİ — Melodi Web / Pastane Golden Master v8.5
═══════════════════════════════════════════════════════════════

NE İŞE YARAR
  WhatsApp ham .jpg linkine önizleme kartı üretmez; og etiketli bir HTML
  ister. Bu script index.html'deki CONFIG'i okur, her ürün için o minik
  HTML dosyasını üretir. 4 ürün de olsa 40 ürün de olsa aynı tek komut.

NASIL ÇALIŞTIRILIR
  1) index.html ile aynı klasöre koy
  2) Terminalde o klasöre gir
  3) python3 og-uret.py

  Windows'ta: py og-uret.py

NE ÜRETİR
  Her ürünün fotoğraf adından türetilmiş bir .html:
     pasta7.jpg  →  pasta7.html
  CONFIG'de o ürüne "og": "baska-ad.html" yazmışsan onu kullanır.

ÖNEMLİ
  • CONFIG'de "siteUrl" ve "ogAuto": true DOLU olmalı.
  • Bu script MEVCUT dosyaların üzerine yazar. Bir og sayfasını elle
    düzenlediysen adını CONFIG'de "og" ile değiştir ki ezilmesin.
  • Yeni ürün eklerken: CONFIG'e ürünü ekle, fotoğrafı klasöre at,
    scripti tekrar çalıştır. Hepsi bu.
═══════════════════════════════════════════════════════════════
"""

import io
import json
import os
import re
import sys

INDEX = "index.html"
IMG_EXT = re.compile(r"\.(jpe?g|png|webp)$", re.I)

TEMPLATE = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} | {site}</title>

<!-- ═══ ÜRÜN ÖNİZLEME SAYFASI — og-uret.py tarafından ÜRETİLDİ ═══
  Elle düzenleme: script tekrar çalışınca bu dosya SIFIRDAN yazılır.
  Kalıcı değişiklik istiyorsan og-uret.py içindeki TEMPLATE'i düzenle.
  Tek işi WhatsApp'a fotoğraflı önizleme kartı verdirmek; ziyaretçi
  linke basınca ana sayfadaki sipariş formuna yönleniyor. -->
<meta property="og:title" content="{name} | {site}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{base}{img}">
<meta property="og:url" content="{base}{page}">
<meta property="og:type" content="product">
<meta name="twitter:card" content="summary_large_image">

<link rel="canonical" href="{base}">
<meta http-equiv="refresh" content="1;url={base}#siparis">
<style>
  body{{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
       background:{bg};color:{text};font-family:system-ui,-apple-system,sans-serif;
       text-align:center;padding:24px}}
  img{{max-width:320px;width:100%;border-radius:14px;display:block;margin:0 auto 18px;
      box-shadow:0 6px 24px rgba(0,0,0,.12)}}
  h1{{font-size:1.25rem;color:{primary};margin:0 0 8px}}
  p{{opacity:.75;margin:0 0 18px;font-size:.95rem}}
  a{{display:inline-block;background:{primary};color:#fff;text-decoration:none;
     padding:13px 26px;border-radius:999px;font-weight:700}}
</style>
</head>
<body>
  <div>
    <img src="{img}" alt="{name}">
    <h1>{name}</h1>
    <p>{desc}</p>
    <a href="{base}#siparis">Sipariş Formuna Git</a>
  </div>
</body>
</html>
"""


def esc(s):
    """meta content içine güvenli koy — tırnak ve < > kaçır."""
    return (str(s or "")
            .replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def config_oku(path):
    html = io.open(path, encoding="utf-8").read()
    m = re.search(r"const CONFIG\s*=\s*(\{.*?\n\});", html, re.S)
    if not m:
        sys.exit("HATA: index.html içinde CONFIG bloğu bulunamadı.")
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError as e:
        sys.exit("HATA: CONFIG geçerli JSON değil (virgül/tırnak hatası?)\n  " + str(e))


def main():
    if not os.path.exists(INDEX):
        sys.exit("HATA: %s bu klasörde yok. Scripti index.html ile aynı yere koy." % INDEX)

    C = config_oku(INDEX)

    base = (C.get("siteUrl") or "").rstrip("/")
    if not base:
        sys.exit('HATA: CONFIG içinde "siteUrl" boş. Sitenin tam adresini yaz.')
    base += "/"

    urunler = C.get("products") or []
    if not urunler:
        sys.exit("HATA: CONFIG içinde products listesi boş.")

    renk = C.get("colors") or {}
    ortak = {
        "site": esc(C.get("name", "")),
        "base": base,
        "primary": renk.get("primary", "#C2185B"),
        "bg": renk.get("bg", "#FFF7FA"),
        "text": renk.get("text", "#3A1E2A"),
    }

    yazilan, atlanan = [], []
    for u in urunler:
        imgs = u.get("imgs") or ([u["img"]] if u.get("img") else [])
        if not imgs:
            atlanan.append((u.get("name", "?"), "fotoğrafı yok"))
            continue

        img = imgs[0]
        page = u.get("og") or IMG_EXT.sub(".html", img)
        if not page.lower().endswith(".html"):
            atlanan.append((u.get("name", "?"), "sayfa adı .html değil: " + page))
            continue

        if not os.path.exists(img):
            print("  ! uyarı: %s klasörde yok (sayfa yine de üretildi)" % img)

        io.open(page, "w", encoding="utf-8").write(TEMPLATE.format(
            name=esc(u.get("name", "")),
            desc=esc(u.get("desc", "")),
            img=img, page=page, **ortak))
        yazilan.append(page)

    print("\n%d sayfa üretildi:" % len(yazilan))
    for p in yazilan:
        print("  +", p)
    if atlanan:
        print("\nAtlanan %d ürün:" % len(atlanan))
        for ad, sebep in atlanan:
            print("  -", ad, "→", sebep)
    print("\nTest: %s%s adresini WhatsApp'ta kendine at, kart çıkıyor mu bak."
          % (base, yazilan[0] if yazilan else ""))
    print("Kart çıkmazsa link sonuna ?v=2 ekle — WhatsApp önizlemeyi cache'liyor.\n")


if __name__ == "__main__":
    main()
