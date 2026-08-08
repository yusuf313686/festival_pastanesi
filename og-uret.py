#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
og-uret.py — index.html içindeki CONFIG'i okur, her ürün için og etiketli
minik bir .html üretir (pasta7.jpg -> pasta7.html).

Neden: WhatsApp ham .jpg linkine önizleme kartı basmaz, og etiketli bir
HTML ister. Bu dosyalar tam olarak onun için var.

Kullanım:
    python og-uret.py                  # index.html'i okur, yanına üretir
    python og-uret.py index.html cikti # farklı dosya / farklı klasör

Not: og:image ve og:url adresleri CONFIG.siteUrl'den türetilir.
siteUrl değişince bu scripti TEKRAR çalıştır, dosyaları yeniden yükle.
"""

import json
import os
import re
import sys

TPL = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">

<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1080">
<meta property="og:image:height" content="1080">
<meta property="og:url" content="{url}">
<meta property="og:type" content="product">
<meta property="og:site_name" content="{site}">
<meta name="twitter:card" content="summary_large_image">

<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url={home}">
<style>
  body{{margin:0;background:#111;color:#eee;font-family:system-ui,sans-serif;
       display:flex;flex-direction:column;align-items:center;justify-content:center;
       min-height:100vh;text-align:center;padding:24px;box-sizing:border-box}}
  img{{max-width:min(420px,90vw);border-radius:16px;margin-bottom:20px}}
  a{{color:#f5b301}}
</style>
</head>
<body>
  <img src="{imgfile}" alt="{title}">
  <h1 style="font-size:20px;font-weight:600">{title}</h1>
  <p>Siparişe yönlendiriliyorsunuz… <a href="{home}">Açılmazsa buraya dokunun</a></p>
  <script>location.replace({home_js});</script>
</body>
</html>
"""


def esc(t):
    return (str(t).replace('&', '&amp;').replace('"', '&quot;')
            .replace('<', '&lt;').replace('>', '&gt;'))


def config_oku(path):
    s = open(path, encoding='utf-8').read()
    a = s.index('const CONFIG = {')
    b = s.index('CONFIG SONU')
    blk = s[a + len('const CONFIG = '):b]
    blk = blk[:blk.rindex('}') + 1]          # kapanış süslüsüne kadar
    blk = re.sub(r'/\*.*?\*/', '', blk, flags=re.S)   # blok yorumları at
    blk = re.sub(r',(\s*[}\]])', r'\1', blk)          # sondaki fazla virgül
    return json.loads(blk)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(src))
    os.makedirs(out, exist_ok=True)

    C = config_oku(src)

    site_url = str(C.get('siteUrl', '')).rstrip('/')
    if not site_url:
        print('HATA: CONFIG.siteUrl boş. Önce onu doldur.')
        sys.exit(1)
    site_url += '/'
    home = site_url + '#urunler'
    site = C.get('name', '')

    urunler = C.get('products') or []
    if not urunler:
        print('HATA: CONFIG.products boş.')
        sys.exit(1)

    uretilen = []
    atlanan = []

    for p in urunler:
        img = p.get('img') or (p.get('imgs') or [None])[0]
        if not img:
            atlanan.append(p.get('name', '?'))
            continue

        # og alanı elle yazılmışsa onu kullan, yoksa foto adından türet
        hedef = p.get('og') or (os.path.splitext(img)[0] + '.html')
        if not hedef.endswith('.html'):
            hedef += '.html'

        ad = p.get('name', '')
        title = f"{ad} | {site}" if site else ad
        desc = p.get('desc') or (f"{site} — {ad}" if site else ad)

        html = TPL.format(
            title=esc(title),
            desc=esc(desc),
            img=esc(site_url + img),
            imgfile=esc(img),
            url=esc(site_url + hedef),
            site=esc(site),
            home=esc(home),
            home_js=json.dumps(home),
        )

        yol = os.path.join(out, hedef)
        with open(yol, 'w', encoding='utf-8') as f:
            f.write(html)
        uretilen.append(hedef)

    print(f"{len(uretilen)} dosya üretildi → {out}")
    for u in uretilen:
        print('  ', u)
    if atlanan:
        print('Fotoğrafı olmadığı için atlananlar:', ', '.join(atlanan))
    print()
    print('og:image adresleri:', site_url + '<foto>.jpg')
    print('Dosyaları repo köküne (index.html ile aynı yere) yükle.')


if __name__ == '__main__':
    main()
