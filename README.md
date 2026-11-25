# Marchand D'Arômes — Regalos Corporativos

Landing de regalos corporativos. El banner es una caja que se abre a medida que
bajás con el scroll; después, dos preguntas y el pedido sale por WhatsApp.
Sitio estático de un solo archivo, sin build y sin dependencias de runtime.

---

## Configuración

El número de WhatsApp que recibe los pedidos se define al comienzo del bloque
SCRIPT de `index.html`:

    const CONFIG = { WHATSAPP: "5491168657847", MARCA: "Marchand D'Arômes" };

Formato internacional, sin el signo más, sin espacios ni guiones. Los celulares
argentinos llevan un 9 después del 54: `+54 9 11 6865-7847` → `5491168657847`.

---

## Deploy en Vercel

El proyecto es estático: Vercel lo detecta solo.

1. **Add New… → Project → Import Git Repository**.
2. Framework Preset `Other`, Root Directory `./`, los tres campos de build vacíos.
3. **Deploy**. Cada push a la rama principal vuelve a publicar.

Dominio propio en **Settings → Domains**, agregando el `CNAME` que indica Vercel.

---

## Estructura

    .
    ├── index.html        # la página entera: HTML + CSS + JS
    ├── banner/           # las dos fotos del hero, 3 anchos c/u (206 KB)
    ├── cajas/            # fotos de los tres tamaños, 4 anchos c/u (490 KB)
    ├── vercel.json       # cleanUrls y headers de seguridad
    ├── .vercelignore     # qué va al repo pero no al deploy
    ├── .gitignore
    ├── README.md
    ├── docs/
    │   └── catalogo.json # referencia: 54 productos con precio e imagen
    └── source/           # material fuente, NO se publica
        ├── banner/           # las dos fotos del hero, sin procesar
        ├── banner-img.py     # regenera banner/
        ├── cajas/            # fotos originales del cliente (JPG/PNG)
        ├── cajas-img.py      # regenera cajas/ desde esos originales
        ├── caja.mov          # video del banner viejo (9,4 MB, HEVC)
        ├── encode-frames.py  # regeneraba los frames de ese banner
        └── README.md         # cómo se hacía

La carpeta `box/`, con los 64 frames del banner animado, **ya no se usa**.
Queda excluida del deploy por `.vercelignore` y se puede borrar del repo.

**Lo que se publica son ~750 KB.** Una visita real baja mucho menos: tanto de
`banner/` como de `cajas/` el navegador elige un solo ancho por foto. En un
celular son ~47 KB del banner y ~130 KB de las tres cajas. El material sin
procesar y el catálogo de referencia están en el repositorio pero excluidos del
deploy por `.vercelignore`: sirven para mantener el proyecto, no para que los
baje un visitante.

---

## El banner

Dos fotos fijas del cliente, una por formato. Reemplazaron al banner animado
que abría una caja cuadro por cuadro: eran 64 WebP y 1,2 MB, contra 47 KB de
la foto que baja un celular hoy.

| Formato | Original | Anchos | Donde |
|---|---|---|---|
| Vertical | 720×1280 (0,56) | 360 / 540 / 720 | hasta 899 px |
| Horizontal | 1280×746 (1,72) | 640 / 960 / 1280 | desde 900 px |

La eleccion la hace `<picture>` con `media`, no JavaScript: es direccion de
arte, no solo resolución, así que tiene que resolverse antes de que el
navegador empiece a bajar nada. Las dos variantes van también en un `preload`
con el mismo `media`, para que el hero no espere al parser.

### Dónde va el texto

Las dos tomas se midieron por franjas, buscando el desvío estándar de cada
una: donde el desvío es bajo hay pared lisa, donde es alto hay producto.

- **La vertical** tiene el 0-33% limpio arriba (sd 8) y el 83-100% limpio abajo
  (sd 8-10), con los productos en el medio. Calza exactamente con el layout que
  ya tenía el hero: título arriba, botón abajo. Medido sobre el render final,
  el texto queda a 16:1 de contraste en el peor 5% de los píxeles que tiene
  detrás.
- **La horizontal** no tiene ninguna franja horizontal limpia: la única zona
  despejada es la columna izquierda. Por eso en escritorio el texto se corre a
  la izquierda y el velo pasa a ser horizontal.

### Por qué el escritorio es a sangre completa

Se probó primero partir la pantalla: panel de texto a la izquierda, foto a la
derecha. No funciona con esta foto. El panel la obliga a un recorte vertical
— a 1440×860 la ventana visible queda en 0,96 contra el 1,72 original — y se
comen el aromatizador y el difusor. Se calculó para anchos de panel del 58 al
70%: recién a partir del 70% entran los productos, y aún así cortan en
pantallas de 1280.

A sangre completa el recorte es mínimo, porque la foto y el viewport son
apaisados los dos:

| Viewport | Recorte |
|---|---|
| 1280×800 | 43 px por lado |
| 1440×860 | 15 px por lado |
| 1920×1080 | 13 px arriba y abajo |

### El velo

El degradado que aclara el fondo del texto no se eligió a ojo. Se midió el
contraste resultante sobre el peor 5% de los píxeles que quedan detrás del
bloque de texto, con cinco intensidades:

| Velo | Peor 5% | |
|---|---|---|
| fuerte | 11,3:1 | apaga el aromatizador |
| **medio** | **7,1:1** | **el que quedó** |
| suave | 4,6:1 | se cae a AA |
| muy suave | 2,6:1 | no pasa |

El "medio" es el más suave que todavía llega a AAA (7:1). Mantiene el color y
el detalle del aromatizador, que con el fuerte quedaba fantasmal.

### Alto del hero

`min-height:100svh`, con `100vh` de fallback. El banner anterior era un sticky
que necesitaba el alto exacto en píxeles y se medía por JS (`--vh`); una foto
fija no lo necesita, así que esa función se eliminó. `svh` es el viewport con
la barra de direcciones a la vista, que es justo lo que hace falta para que el
botón entre sin scrollear.

### Para cambiar las fotos

Reemplazar `source/banner/vertical.webp` y `source/banner/horizontal.webp` y
correr:

    python source/banner-img.py source/banner banner

El script no reencuadra ni retoca: las tomas ya vienen compuestas. Solo genera
los anchos, y **no agranda por encima del original**. Si las fotos nuevas
tienen otra proporción, conviene volver a medir las franjas antes de dar por
buena la posición del texto.

## Las cajas y el formulario

El producto son **tres tamaños de caja** con contenido fijo, no combos armados
a medida:

| Caja | Productos | Contenido |
|---|---|---|
| Chica | 2 | Vela Aromática, Crema de Manos |
| Mediana | 3 | Crema de Cuerpo, Jabón Líquido para Manos, Perfume de Ambientes |
| Grande | 4 | Crema de Cuerpo, Vela Aromática, Perfume de Ambientes, Difusor de Varillas |

Esta lista **se leyó de las fotos que mandó el cliente**, producto por producto,
para que el texto diga exactamente lo que se ve en la imagen. Reemplaza a la
lista provisoria anterior, que venía de los ejemplos del borrador y ya no
coincidía con el material. Igual conviene que el cliente la confirme.

El contenido vive en la constante `CAJAS`, dentro del bloque 2 del script. Cada
caja tiene un array `incluye` que alimenta tres cosas a la vez: la tarjeta de la
sección "Las cajas", el texto `alt` de la foto y la línea *Incluye* del mensaje
de WhatsApp. Se edita en un solo lugar y los tres quedan al día.

### Las fotos

En `cajas/`, una por tamaño, en cuatro anchos (320 / 480 / 720 / 960) para que
el navegador baje solo el que necesita:

| Caja | Original |
|---|---|
| Chica | `Caja chica.jpg` |
| Mediana | `caja mediana 1.jpg` |
| Grande | `caja grande 1.jpg` |

De las seis fotos que llegó el cliente se eligieron estas tres por dos razones:
el conteo de productos coincide con el tamaño que ilustran, y las tres están
sobre fondo claro parejo. Las descartadas (`caja mediana 2`, `caja grande 2`)
quedaron en `source/cajas/`: la mediana 2 muestra cuatro productos y la grande 2
tiene una dominante cálida que rompe la serie.

#### El reencuadre

Las tres tomas venían con encuadres distintos: márgenes dispares y la caja más
grande o más chica dentro del cuadro según la toma. Una al lado de la otra se
notaba poco, pero apiladas en un celular se leían como tres fotos sueltas, con
la Caja Chica ocupando más cuadro que la Grande.

`source/cajas-img.py` las normaliza. Para cada foto:

1. **Detecta el fondo** como la mediana de las cuatro esquinas.
2. **Detecta el contenido real** contando píxeles distintos del fondo por fila y
   por columna, no píxel suelto: así el viñeteado suave de los bordes — que en
   la mediana llega hasta el borde mismo — no cuenta como contenido.
3. **Reescala la foto entera** hasta que ese contenido ocupe 88% del alto o 92%
   del ancho, lo que primero tope.
4. **La apoya sobre una línea de base común** al 95% del alto, centrada en el
   contenido y no en el cuadro original.
5. **Corre el punto blanco** a `rgb(245, 242, 237)`.

El paso 3 reescala la foto completa y la desplaza, en vez de recortar el
contenido y pegarlo sobre un fondo liso. La primera versión hacía lo segundo y
en la mediana se veía el borde del recorte como un rectángulo más oscuro, por
el viñeteado. Al escalar entera, el degradé llega al borde del cuadro como en
el original y no hay costura. Las tres escalas quedan entre ×1,21 y ×1,46, así
que el 960 final no inventa detalle sobre originales de 1000 px.

El punto blanco del paso 5 es un ajuste de temperatura, no un filtro: multiplica
los tres canales por una constante cada uno, así que no altera el color relativo
de los productos. Baja el blanco puro de las fotos al beige de la página, para
que la imagen se integre con la tarjeta en vez de aparecer como un rectángulo
blanco. Para desactivarlo, `PUNTO_BLANCO = None` en el script; si se cambia, hay
que mover también el `bg` de las tres cajas y el fondo de `.caja__img`, que
están en ese mismo color para que el relleno no se note.

Las tarjetas pasaron de 4:3 a **1:1** para acompañar a las fotos.

    python source/cajas-img.py source/cajas cajas

El cartel de "Caja elegida" pasó a fondo negro porque el dorado no se leía
sobre el fondo claro de las fotos.

### El formulario

Dos preguntas, sin datos de contacto:

1. **¿Para cuántas personas?** — 10 a 29 / 30 a 49 / 50 o más
2. **¿Qué caja querés?** — Chica / Mediana / Grande

La segunda pregunta tiene **dos entradas sincronizadas**: los tres botones del
formulario y las tres tarjetas de la sección "Las cajas", que son botones de
verdad (`<button aria-pressed>`). Se elija donde se elija, `ponerCaja()` deja
las dos vistas en el mismo estado. Si alguien elige desde la tarjeta y todavía
no respondió cuántas personas, la página lo baja sola al formulario.

Con las dos respuestas aparece el bloque de cierre y la barra fija de WhatsApp.
El mensaje queda así:

    Hola Marchand D'Arômes
    Quiero armar un pedido de *regalos corporativos*.
    *Caja:* Caja Mediana (3 productos)
    *Incluye:* Crema de Manos, Jabón Líquido, Vela Aromática
    *Para:* 30 a 49 personas
    ¿Me arman una propuesta?

### Decisiones sobre esta versión

- **Se eliminó la pregunta de presupuesto.** Al elegir la caja directamente, el
  rango de inversión queda implícito y no hay que publicar montos que todavía
  no están confirmados. También desaparecieron las preguntas de público y fecha,
  junto con la sugerencia automática de aromas: menos fricción, más gente
  llegando al chat.
- **El contenido de las cajas es provisorio.** Se tomaron los productos que ya
  figuraban como ejemplo. **Pendiente de confirmar con el cliente** antes de
  publicar.
- **La nota de los 15 días** pasó a colgar de la pregunta 2, que es donde
  quedaba el último texto del formulario.
- **El FAQ cierra empujando al chat.** El título dejó de ser "Antes de
  escribirnos" — que frenaba — y pasó a "Lo que más nos preguntan", con un
  botón de WhatsApp al pie de la lista para quien no encuentre su respuesta.

### Sello Empresa B

En el pie, dentro de `.sello`. Es un **SVG dibujado a mano, no el archivo
oficial de Sistema B**: sirve para ver el bloque en su lugar y con las
proporciones correctas.

> **Antes de publicar:** reemplazar por el logotipo oficial que entrega Sistema
> B y verificar que la certificación de la empresa esté vigente. El sello es una
> marca registrada con condiciones de uso propias, y mostrarlo sin certificación
> vigente es una afirmación comercial falsa.

El reemplazo es directo: cambiar el `<svg>` por un `<img src="...">` dentro de
`.sello`, que ya tiene el tamaño y la alineación resueltos.

## Móvil

- Todos los objetivos táctiles llegan a 44 px.
- La barra fija de WhatsApp respeta el notch (`env(safe-area-inset-bottom)`) y
  el body suma padding para no tapar el footer.
- El hero mide `100svh`: una pantalla exacta, con el título sobre la pared
  limpia de arriba y el botón sobre el mármol de abajo.
- La foto del banner en celular es la vertical, 47 KB.
- Las fotos de las cajas se sirven desde el repo en el ancho que corresponde
  (`srcset`): en un celular son ~130 KB las tres.

Todo el movimiento se desactiva con `prefers-reduced-motion: reduce`. Desde que
el banner es una foto fija, lo único que queda por desactivar son las
transiciones de aparición de las secciones.

---

## Puntos abiertos

- **Del CDN de Tiendanube ya solo cuelga el logotipo** (cabecera, pie y
  favicon). Las fotos de las cajas pasaron a ser propias y viven en el repo, así
  que una baja de productos en la tienda ya no afecta a esta página.

- **Sello Empresa B:** el SVG del pie es un dibujo propio, no el archivo
  oficial. Hay que reemplazarlo y confirmar que la certificación esté vigente.

- **Contenido de las cajas:** la lista sale de leer las fotos del cliente, no de
  una lista que haya pasado por escrito. Vale confirmarla, sobre todo los
  nombres comerciales exactos ("Perfume de Ambientes" figura en el envase como
  *Parfums pour la Maison*).

- **Contenido comercial asumido, pendiente de validación:** plazos de 7 a 15
  días hábiles, presupuesto en 24 hs. Están en el banner y en el FAQ.

- **Resolución de las fotos del banner.** La vertical es 720×1280 y la
  horizontal 1280×746. Alcanzan para un celular y para un monitor de 1440,
  pero en una pantalla 2K la horizontal se estira al doble y se va a ver
  blanda. Si el cliente tiene los originales en mayor resolución, conviene
  pedirlos: es cambiar dos archivos y correr el script.

- **Verificar en un teléfono real.** El panel de previsualización usado durante
  el desarrollo no renderiza en continuo — no corre `IntersectionObserver` y no
  rasteriza imágenes — así que la verificación fue por medición del DOM y por
  simulación del recorte y el contraste, no por captura de la página armada.
  Conviene recorrerla en un celular una vez publicada.

- **Sin analítica.** Si se quiere medir conversión, el punto natural es un
  evento en el click del botón de WhatsApp.

---

## Licencia de Vercel

El plan Hobby es gratis pero **no permite uso comercial**. Si esto pasa a ser un
canal de ventas formal del cliente, corresponde el plan Pro.
