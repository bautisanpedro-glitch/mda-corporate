# -*- coding: utf-8 -*-
"""
Prepara las dos fotos del banner.

No reencuadra ni retoca: las tomas ya vienen compuestas con la pared limpia
arriba y los productos abajo, que es justo lo que necesita el overlay. Solo
genera los anchos del srcset.

No agranda por encima del original: la vertical llega hasta 720 y la
horizontal hasta 1280, que es lo que midieron los archivos que mando el
cliente.

Uso:  python source/banner-img.py source/banner banner
"""
import os, sys
from PIL import Image

ORIG = sys.argv[1]
DEST = sys.argv[2]

JUEGOS = [
    ("vertical.webp",   "v", [360, 540, 720]),    # celular
    ("horizontal.webp", "h", [640, 960, 1280]),   # escritorio
]

if not os.path.isdir(DEST):
    os.makedirs(DEST)

total = 0
for arch, slug, anchos in JUEGOS:
    im = Image.open(os.path.join(ORIG, arch)).convert("RGB")
    print("%-16s original %dx%d  (%.2f)" % (arch, im.width, im.height, im.width/im.height))
    for w in anchos:
        if w > im.width:
            print("   %4d  OMITIDO: mas grande que el original" % w)
            continue
        h = int(round(im.height * w / float(im.width)))
        chico = im.resize((w, h), Image.LANCZOS)
        salida = os.path.join(DEST, "%s-%d.webp" % (slug, w))
        chico.save(salida, "WEBP", quality=82, method=6)
        kb = os.path.getsize(salida)/1024
        total += kb
        print("   %-14s %4dx%-4d  %6.1f KB" % (os.path.basename(salida), w, h, kb))
    print()

print("TOTAL %.0f KB" % total)
