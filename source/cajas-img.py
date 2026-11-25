# -*- coding: utf-8 -*-
"""
Prepara las fotos de las tres cajas para la web.

El problema que resuelve: los originales vienen con encuadres distintos
(margenes dispares, la caja mas grande o mas chica en el cuadro segun la toma).
Puestos uno debajo del otro en un celular, se leen como tres fotos sueltas y no
como una serie.

Que hace, para cada foto:
  1. detecta el fondo (mediana de las cuatro esquinas) y el contenido real,
     por columnas y filas, para ignorar el vineteado suave de los bordes;
  2. recorta al contenido;
  3. lo reescala hasta ocupar un alto y un ancho objetivo dentro del cuadrado;
  4. lo apoya sobre una linea de base comun, centrado horizontalmente;
  5. corre el punto blanco hacia el beige de la pagina, para que la foto se
     integre con la tarjeta en vez de aparecer como un rectangulo blanco.

Uso:  python source/cajas-img.py source/cajas cajas
"""
import os, sys
from PIL import Image

ORIG = sys.argv[1]
DEST = sys.argv[2]

SEL = [
    ("Caja chica.jpg",     "chica"),
    ("caja mediana 1.jpg", "mediana"),
    ("caja grande 1.jpg",  "grande"),
]

ANCHOS    = [320, 480, 720, 960]
LADO      = 1200    # lienzo de trabajo
ANCHO_MAX = 0.92    # el contenido no pasa de este ancho
ALTO_MAX  = 0.88    # ni de este alto
BASE      = 0.95    # donde apoya el contenido
PUNTO_BLANCO = (245, 242, 237)   # None para dejar el blanco original


def fondo(im):
    w, h = im.size; m = 40; px = im.load(); e = []
    for cx, cy in [(0,0), (w-m,0), (0,h-m), (w-m,h-m)]:
        for y in range(cy, cy+m, 4):
            for x in range(cx, cx+m, 4):
                e.append(px[x, y])
    return tuple(sorted(p[i] for p in e)[len(e)//2] for i in range(3))


def recuadro(im, bg, umbral=24):
    """Caja del contenido real. Cuenta por fila y por columna para que el
    vineteado de los bordes, que es suave y continuo, no cuente como contenido."""
    w, h = im.size; px = im.load()
    col = [0]*w; fil = [0]*h
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            p = px[x, y]
            if max(abs(p[i]-bg[i]) for i in range(3)) > umbral:
                col[x] += 1; fil[y] += 1
    minC = max(3, int(h*0.006))
    minF = max(3, int(w*0.006))
    xs = [x for x in range(w) if col[x] >= minC]
    ys = [y for y in range(h) if fil[y] >= minF]
    if not xs or not ys:
        return (0, 0, w, h)
    return (min(xs), min(ys), max(xs)+1, max(ys)+1)


def balance(im, blanco):
    """Corre el punto blanco. Es un ajuste de temperatura, no un filtro:
    toca todos los canales por igual en proporcion, asi que no altera el
    color relativo de los productos."""
    tabla = []
    for c in range(3):
        k = blanco[c] / 255.0
        tabla += [int(round(i * k)) for i in range(256)]
    return im.point(tabla)


print("%-10s %-22s %-22s %s" % ("caja", "contenido original", "en el cuadro", "escala"))
print("-" * 76)

total = 0
for arch, slug in SEL:
    im = Image.open(os.path.join(ORIG, arch)).convert("RGB")
    bg = fondo(im)
    x0, y0, x1, y1 = recuadro(im, bg)
    recorte = im.crop((x0, y0, x1, y1))
    cw, ch = recorte.size

    # la escala la fija el lado que primero toca su limite
    k = min(LADO*ANCHO_MAX / cw, LADO*ALTO_MAX / ch)
    nw, nh = int(round(cw*k)), int(round(ch*k))

    # Se reescala la foto ENTERA y se la corre, en vez de recortar el contenido
    # y pegarlo sobre un fondo liso: algunas tomas tienen un vineteado suave y
    # el recorte pegado dejaba ver su borde como un rectangulo mas oscuro.
    grande_ = im.resize((int(round(im.width*k)), int(round(im.height*k))), Image.LANCZOS)
    ox = int(round(LADO/2.0 - (x0+x1)/2.0*k))
    oy = int(round(LADO*BASE - y1*k))

    lienzo = Image.new("RGB", (LADO, LADO), bg)
    lienzo.paste(grande_, (ox, oy))

    if PUNTO_BLANCO:
        lienzo = balance(lienzo, PUNTO_BLANCO)

    print("%-10s %4dx%-4d (%3.0f%% x %3.0f%%)  %4dx%-4d (%3.0f%% x %3.0f%%)  x%.2f"
          % (slug, cw, ch, cw/im.width*100, ch/im.height*100,
             nw, nh, nw/LADO*100, nh/LADO*100, k))

    for w in ANCHOS:
        chico = lienzo.resize((w, w), Image.LANCZOS)
        salida = os.path.join(DEST, "%s-%d.webp" % (slug, w))
        chico.save(salida, "WEBP", quality=82, method=6)
        total += os.path.getsize(salida)/1024

if PUNTO_BLANCO:
    print("\npunto blanco -> rgb%s" % (PUNTO_BLANCO,))
print("TOTAL %.0f KB" % total)
