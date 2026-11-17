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
    ├── box/              # 64 frames WebP de la caja abriéndose (1,2 MB)
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

**Lo que se publica son ~1,3 MB**, casi todo la secuencia del banner. El video original y el catálogo de referencia
están en el repositorio pero excluidos del deploy por `.vercelignore`: sirven
para mantener el proyecto, no para que los baje un visitante.

---

## El banner: la caja que se abre

Ocupa la pantalla completa y se abre a medida que bajás. Es lo primero y lo
único que se ve al entrar.

### De dónde salen los frames

El video original (`.mov`, 2,6 s, 2160×3840, **HEVC**) no sirve para la web:
Chrome y Firefox no decodifican HEVC de forma confiable. Por eso el banner **no
usa video**, sino 64 imágenes WebP (660×1172, 1,2 MB en total) dibujadas sobre
un canvas.

Los frames no están repartidos por tiempo sino **por movimiento acumulado**: se
mide la diferencia entre frames consecutivos y se eligen 64 a intervalos iguales
de movimiento. Así el scroll avanza parejo y no se gastan frames donde la caja
está quieta.

### Cómo funciona

    progreso = -stage.top / (stage.alto - alto_viewport)   // 0 a 1
    posicion = progreso × 63                               // con decimales

La sección `.stage` mide 250vh (230vh en mobile) y adentro tiene un bloque
`position:sticky` de un viewport de alto. Ese alto extra es el recorrido que
alimenta la animación: unos 1050 px, es decir ~16 px de scroll por frame.

Tres cosas hacen que se sienta fluido y no a los saltos:

1. **Mezcla entre frames vecinos.** `posicion` tiene decimales: se dibuja el
   frame entero y encima el siguiente con `globalAlpha` igual a la parte
   decimal. Con eso 64 imágenes se ven como un movimiento continuo.
2. **Amortiguación.** El valor dibujado persigue al del scroll con un factor de
   0,2 por cuadro. El scroll de los celulares llega a tirones; esto lo suaviza.
3. **`ImageBitmap`.** Los frames se bajan con `fetch` y se convierten con
   `createImageBitmap`, que entrega el mapa de bits ya decodificado. Dibujar un
   `ImageBitmap` no bloquea el hilo principal; dibujar un `<img>` sí puede.

El dibujado corre en un lazo de `requestAnimationFrame` que lee la posición del
scroll en cada cuadro, en lugar de reaccionar al evento `scroll` (que en iOS
llega con menos frecuencia durante el desplazamiento por inercia). El lazo se
pausa cuando el hero sale de pantalla.

### Carga

El frame 0 está precargado con `<link rel=preload>` y es el LCP. El resto entra
de a tandas de 6, **en orden de subdivisión**: primero los extremos, después los
medios, después el relleno. Si alguien scrollea antes de que termine, se dibuja
el frame más cercano que ya esté disponible, así que la animación nunca muestra
un hueco: arranca tosca y se afina.

### El texto

Casi no hay. Un título mientras la caja está cerrada, **nada en todo el tramo en
que se abre**, y el botón al final. Las opacidades se calculan con el progreso
del scroll, no con clases.

| progreso | título | botón |
|---|---|---|
| 0 → 0,12 | visible | — |
| 0,12 → 0,30 | se va | — |
| 0,30 → 0,64 | — | — |
| 0,64 → 0,82 | — | aparece |
| 0,82 → 1 | — | visible |

> **Red de seguridad.** El botón arranca en `opacity:0` y lo muestra el lazo. Si
> `requestAnimationFrame` no corriera (pestaña en segundo plano al cargar,
> webview raro), a los 1,5 s se muestran título y botón igual. El punto de
> conversión no puede quedar invisible.

### Para cambiar el video

El original y el script que genera la secuencia están en `source/`. La receta
completa está en [source/README.md](source/README.md).

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
