# -*- coding: utf-8 -*-
"""
Prepara las fotos de las tres cajas para la web.

No recorta: rellena hasta el cuadrado con el color de fondo real de la foto,
para que las tres queden con la misma proporcion sin perder nada de la
composicion. Exporta WebP en cuatro anchos para el srcset.
"""
import io, os, sys
from PIL import Image

ORIG = sys.argv[1]
DEST = sys.argv[2]

SEL = [
    ("Caja chica.jpg",    "chica"),
    ("caja mediana 1.jpg", "mediana"),
    ("caja grande 1.jpg",  "grande"),
]
ANCHOS = [320, 480, 720, 960]

if not os.path.isdir(DEST):
    os.makedirs(DEST)

def fondo(im):
    """Color de fondo = mediana de las cuatro esquinas (muestra de 40x40)."""
    w, h = im.size
    m = 40
    cajas = [(0,0,m,m), (w-m,0,w,m), (0,h-m,m,h), (w-m,h-m,w,h)]
    px = []
    for c in cajas:
        r = im.crop(c)
        px.extend(list(r.getdata()))
    canal = lambda i: sorted(p[i] for p in px)[len(px)//2]
    return (canal(0), canal(1), canal(2))

total = 0
for arch, slug in SEL:
    im = Image.open(os.path.join(ORIG, arch)).convert("RGB")
    bg = fondo(im)
    lado = max(im.size)
    cuadro = Image.new("RGB", (lado, lado), bg)
    cuadro.paste(im, ((lado - im.width)//2, (lado - im.height)//2))

    for w in ANCHOS:
        chico = cuadro.resize((w, w), Image.LANCZOS)
        salida = os.path.join(DEST, "%s-%d.webp" % (slug, w))
        chico.save(salida, "WEBP", quality=80, method=6)
        kb = os.path.getsize(salida)/1024
        total += kb
        print("%-18s %4dx%-4d  %6.1f KB" % (os.path.basename(salida), w, w, kb))
    print("   fondo %s  original %dx%d\n" % (bg, im.width, im.height))

print("TOTAL %.0f KB" % total)
