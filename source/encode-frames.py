# -*- coding: utf-8 -*-
"""Elige N frames repartidos por movimiento acumulado y los encodea a WebP."""
import glob, os, sys
from PIL import Image, ImageChops, ImageStat

ORIGEN = sys.argv[1]
DESTINO = sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 48
ANCHO = int(sys.argv[4]) if len(sys.argv) > 4 else 480
CALIDAD = int(sys.argv[5]) if len(sys.argv) > 5 else 72

if not os.path.isdir(DESTINO):
    os.makedirs(DESTINO)

fs = sorted(glob.glob(os.path.join(ORIGEN, 'g*.jpg')))
fs = fs[:91]                      # los ultimos son estaticos, no aportan

# --- perfil de movimiento acumulado ---
prev, acum, curva = None, 0.0, []
for f in fs:
    chico = Image.open(f).convert('L').resize((120, 213))
    if prev is not None:
        acum += ImageStat.Stat(ImageChops.difference(chico, prev)).mean[0]
    curva.append(acum)
    prev = chico
total = curva[-1]

# --- elegir N frames a intervalos iguales de movimiento ---
elegidos, j = [], 0
for k in range(N):
    objetivo = total * k / (N - 1)
    while j < len(curva) - 1 and curva[j] < objetivo:
        j += 1
    if not elegidos or elegidos[-1] != j:
        elegidos.append(j)
    else:
        nj = min(j + 1, len(curva) - 1)
        if nj != elegidos[-1]:
            elegidos.append(nj)

# --- encodear ---
total_bytes = 0
for idx, src in enumerate(elegidos):
    im = Image.open(fs[src]).convert('RGB')
    w, h = im.size
    alto = int(round(ANCHO * h / float(w)))
    alto -= alto % 2
    im = im.resize((ANCHO, alto), Image.LANCZOS)
    ruta = os.path.join(DESTINO, 'b%02d.webp' % idx)
    im.save(ruta, 'WEBP', quality=CALIDAD, method=6)
    total_bytes += os.path.getsize(ruta)

print('frames originales : %d' % len(fs))
print('frames elegidos   : %d  (indices %s ... %s)' % (len(elegidos), elegidos[:5], elegidos[-3:]))
print('tamanio           : %dx%d' % (ANCHO, alto))
print('peso total        : %.0f KB  (%.1f KB por frame)'
      % (total_bytes / 1024.0, total_bytes / 1024.0 / len(elegidos)))
