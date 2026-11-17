# Marchand D'Arômes — Regalos Corporativos

Landing de regalos corporativos. El banner es una caja que se abre a medida que
bajás con el scroll; después, dos preguntas y el pedido sale por WhatsApp.
Sitio estático de un solo archivo, sin build y sin dependencias de runtime.

---

## Configuración

El número de WhatsApp que recibe los pedidos se define al comienzo del bloque
SCRIPT de `index.html`:

    const CONFIG = { WHATSAPP: "5491169835444", MARCA: "Marchand D'Arômes" };

Formato internacional, sin el signo más, sin espacios ni guiones. Los celulares
argentinos llevan un 9 después del 54: `+54 9 11 6983-5444` → `5491169835444`.

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
    ├── box/              # 48 frames WebP de la caja abriéndose (680 KB)
    ├── vercel.json       # cleanUrls y headers de seguridad
    ├── .vercelignore     # qué va al repo pero no al deploy
    ├── .gitignore
    ├── README.md
    ├── docs/
    │   └── catalogo.json # referencia: 54 productos con precio e imagen
    └── source/           # material fuente, NO se publica
        ├── caja.mov          # video original (9,4 MB, HEVC)
        ├── encode-frames.py  # regenera la secuencia de frames
        └── README.md         # cómo rehacerla

**Lo que se publica son 865 KB.** El video original y el catálogo de referencia
están en el repositorio pero excluidos del deploy por `.vercelignore`: sirven
para mantener el proyecto, no para que los baje un visitante.

---

## El banner: la caja que se abre

### De dónde salen los frames

El video original (`.mov`, 2,6 s, 2160×3840, **HEVC**) no sirve para la web:
Chrome y Firefox no decodifican HEVC de forma confiable. Por eso el banner **no
usa video**, sino una secuencia de 48 imágenes WebP que se dibujan en un canvas.

Los frames no están repartidos por tiempo sino **por movimiento acumulado**: se
midió la diferencia entre frames consecutivos y se eligieron 48 a intervalos
iguales de movimiento. Así el scroll avanza parejo y no se gastan frames en los
tramos donde la caja está quieta.

### Cómo funciona

    progreso = -stage.top / (stage.alto - alto_viewport)   // 0 a 1
    frame    = round(progreso × 47)

La sección `.stage` mide 300vh (260vh en mobile) y adentro tiene un bloque
`position:sticky` de un viewport de alto. Ese alto extra es el recorrido de
scroll que alimenta la animación.

El dibujado va por `requestAnimationFrame`, y si el frame exacto todavía no se
descargó se pinta el más cercano que sí esté, para no dejar huecos en blanco.
La carga es progresiva: primero el frame 0 (que es el LCP y está precargado con
`<link rel=preload>`), después el resto de a tandas de 6.

### Para cambiar el video

El original y el script que genera la secuencia están en `source/`. La receta
completa, con los comandos, está en [source/README.md](source/README.md).

---

## Las dos preguntas

Son solo dos, sin formulario ni datos de contacto:

1. **Cuánto invertir por regalo** — cuatro rangos.
2. **Cuántos regalos** — cuatro tramos de cantidad.

Los combos salen de un mapa directo `presupuesto → 3 combos`, en la constante
`COMBOS` del script. No hay motor de scoring: con dos preguntas no hacía falta,
y un mapa explícito es más fácil de curar comercialmente.

Para cambiar la oferta se edita `COMBOS`. Cada entrada define nombre, etiqueta,
qué incluye, una línea de argumento y la foto:

    { nom:"Rituel Maison", band:"Más pedido",
      items:["Arôme Diffuseur con varillas","Vela Aromática"],
      why:"Aroma continuo más el ritual de encender.",
      img:"difusor-....webp" }

El botón de WhatsApp aparece recién cuando hay un combo elegido, dice
explícitamente qué se va a pedir ("Pedir Rituel Maison por WhatsApp") y en
mobile queda fijo abajo. El mensaje se arma con combo, cantidad y rango.

---

## Móvil

- Todos los objetivos táctiles llegan a 44 px.
- La barra fija de WhatsApp respeta el notch (`env(safe-area-inset-bottom)`) y
  el body suma padding para no tapar el footer.
- El alto del viewport se mide por JS (`--vh`) en lugar de usar `svh`/`dvh`:
  varían entre navegadores y con la barra de direcciones, y acá la caja tiene
  que entrar sí o sí junto al texto.
- Las fotos de los combos se piden al CDN en el ancho que corresponde (`srcset`).

Todo el movimiento se desactiva con `prefers-reduced-motion: reduce`; en ese
caso la caja se muestra abierta y la sección deja de ser sticky.

---

## Puntos abiertos

- **Las fotos de producto se sirven desde el CDN de Tiendanube.** Se mantienen
  en sincronía con la tienda, pero si se migra de plataforma o se dan de baja
  productos, esas URLs dejan de responder. Los frames de la caja, en cambio,
  viven en el repo. Decisión tomada a conciencia.

- **Contenido comercial asumido, pendiente de validación:** plazos de 7 a 15
  días hábiles, presupuesto en 24 hs, entrega multi-sede. Están en la sección
  "Cómo sigue".

- **Verificar en un teléfono real.** El panel de previsualización usado durante
  el desarrollo no renderiza en continuo: no corren `requestAnimationFrame` ni
  `IntersectionObserver`. Se validó el estado final de cada pantalla y la
  aritmética del scroll forzando el dibujado a mano, pero no la fluidez de la
  animación. Conviene recorrer la página en un celular una vez publicada.

- **Sin analítica.** Si se quiere medir conversión, el punto natural es un
  evento en el click del botón de WhatsApp.

---

## Licencia de Vercel

El plan Hobby es gratis pero **no permite uso comercial**. Si esto pasa a ser un
canal de ventas formal del cliente, corresponde el plan Pro.
