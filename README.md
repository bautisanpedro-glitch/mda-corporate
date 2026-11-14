# Marchand D'Arômes — Regalos Corporativos

Landing de regalos corporativos con configurador de kits y derivación a WhatsApp con el
pedido ya armado. Sitio estático de un solo archivo, sin build y sin dependencias de runtime.

---

## Configuracion

El numero de WhatsApp que recibe los pedidos se define al comienzo del bloque
SCRIPT de index.html:

    const CONFIG = {
      WHATSAPP: "5491169835444",
      MARCA: "Marchand D'Aromes"
    };

Formato internacional, sin el signo mas, sin espacios ni guiones. Los celulares
argentinos llevan un 9 despues del 54:

    +54 9 11 6983-5444  ->  5491169835444

Si alguna vez cambia la linea comercial, se edita ahi y listo: no hay otro lugar
del codigo donde el numero este escrito.

---

## Deploy en Vercel

El proyecto es estático: Vercel lo detecta solo, sin framework ni comando de build.

### Opción A — desde GitHub (recomendada)

1. Crear el repositorio en GitHub y subir el contenido de esta carpeta
   (`index.html`, `vercel.json`, `.gitignore`, `docs/`, `README.md`).
2. En Vercel: **Add New… → Project → Import Git Repository**.
3. Dejar la configuración por defecto:

   | Campo | Valor |
   |---|---|
   | Framework Preset | `Other` |
   | Root Directory | `./` |
   | Build Command | *(vacío)* |
   | Output Directory | *(vacío)* |
   | Install Command | *(vacío)* |

4. **Deploy**. Cada push a la rama principal vuelve a publicar automáticamente.

### Opción B — drag & drop

Comprimir la carpeta y arrastrarla a `vercel.com/new`. Sirve para una prueba rápida,
pero pierde el redeploy automático.

### Dominio

En **Settings → Domains** se puede apuntar un subdominio propio, por ejemplo
`corporativo.marchandaromes.com.ar`, agregando el registro `CNAME` que indica Vercel
en el DNS del dominio.

---

## Estructura

```
.
├── index.html          # la página completa: HTML + CSS + JS en un solo archivo
├── vercel.json         # cleanUrls y headers de seguridad
├── .gitignore
├── README.md
└── docs/
    └── catalogo.json   # referencia: 54 productos con nombre, precio e imagen
```

---

## Mantenimiento

Todo lo editable vive en el `<script>` de `index.html`, en tres objetos consecutivos.

### 1. Precios — objeto `P`

```js
const P = {
  manos50: { n:"Crème Pour Les Mains 50 g", p: 8500 },
  ...
};
```

Los precios **no se muestran en pantalla**: se usan solo para calcular la banda
(`$` / `$$` / `$$$`) y para filtrar los kits según el presupuesto elegido.
Al actualizar la lista de precios, el motor de recomendación se recalibra solo.

### 2. Kits — array `KITS`

Cada kit declara su composición, su universo y las ocasiones para las que aplica:

```js
{ id:"rituel-maison", nom:"Rituel Maison", sub:"Difusor + vela",
  items:["difusor","vela"],              // claves del objeto P
  tags:["hogar","velas"],                // perfumeria | cosmetica | hogar | velas
  occ:["vip","fin-ano","reconocimiento"],
  img:"...webp", bg:"#000",
  desc:"..." }
```

Agregar un kit es sumar un objeto al array: no hay que tocar el motor.

### 3. Motor de recomendación — función `puntaje()`

Pondera, en este orden de peso:

1. **Ajuste al presupuesto** — tolerancia asimétrica: acepta hasta 30 % por debajo
   del rango y 25 % por encima; más lejos que eso, descarta el kit.
2. **Afinidad de universo** — coincidencia entre los `tags` del kit y lo elegido.
3. **Ocasión** — si el kit está pensado para ese motivo.
4. **Logística por volumen** — en pedidos de +100 unidades penaliza los kits de tres
   piezas y premia los de pieza única, que escalan mejor en armado.

Devuelve las 3 mejores opciones. Las 576 combinaciones posibles del formulario
fueron verificadas: todas devuelven 3 resultados coherentes.

---

## Móvil y animaciones

La página está pensada para que el grueso del tráfico entre desde un celular.

### Decisiones de móvil

- Los campos del formulario usan **16 px** en pantallas chicas. Es el mínimo que evita
  que iOS haga zoom automático al enfocar un input — un zoom que descoloca el layout y
  en la práctica expulsa al usuario del formulario.
- Teclados correctos por campo (`inputmode`, `enterkeyhint`, `autocapitalize`): el de
  email muestra la arroba, el de teléfono abre el teclado numérico.
- Todos los objetivos táctiles llegan a **44 px** de alto, incluidos el botón *Volver*
  y los enlaces del pie, que antes medían 16 px.
- La barra de WhatsApp respeta el notch (`env(safe-area-inset-bottom)`) y el `body`
  suma padding inferior para que la barra no tape el footer.
- Las fotos se piden al CDN en el ancho que corresponde (`srcset` de 240 a 640 px).
  Un celular baja el hero en 640 px en lugar de 1024: unos **45 KB menos**.
- `preconnect` al CDN de imágenes, además del de fuentes.

### Animaciones

Son deliberadamente sobrias: la marca es perfumería francesa, no una landing de SaaS.
Todo el movimiento usa `transform` y `opacity`, que el navegador resuelve en el
compositor sin recalcular layout.

- Revelado progresivo de secciones al entrar en pantalla (`IntersectionObserver`).
- Transición direccional entre pasos del configurador: avanza hacia la izquierda,
  retrocede hacia la derecha.
- Cascada escalonada en opciones, chips y tarjetas de resultado.
- Header que se condensa al bajar, barra de progreso que se llena, y el `+` del FAQ
  que gira 135° hasta volverse una cruz.

> **Dos redes de seguridad.** El revelado es decorativo, pero esconde contenido, así que
> no puede fallar. Primero: el hero se revela al cargar, sin depender del observer.
> Segundo: si a los 1,2 s el observer no reveló nada, se muestra todo de una. En el peor
> caso el contenido aparece sin animación; nunca queda invisible.

Todo el movimiento se desactiva con `prefers-reduced-motion: reduce`.

> **Pendiente de verificar en un dispositivo real.** El panel de previsualización usado
> durante el desarrollo no renderiza de forma continua, así que las transiciones no
> avanzan entre capturas: se validó el estado final de cada pantalla, no el tiempo ni la
> suavidad de las animaciones. Conviene recorrer la página en un teléfono una vez
> publicada.

## Puntos abiertos

- **Imágenes servidas desde el CDN de Tiendanube.** Las fotos se referencian
  directamente desde `acdn-us.mitiendanube.com`. Funciona hoy y se mantiene en sincronía
  con la tienda, pero si se migra de plataforma o se dan de baja productos, esas URLs
  dejan de responder. Si se quiere independencia total, hay que descargar las 16 imágenes
  a `/img` y reemplazar la constante `IMG` del script.

- **Contenido comercial asumido, pendiente de validación.** Están escritos en el FAQ y en
  la sección "Cómo trabajamos" y conviene confirmarlos antes de publicar:
  mínimo de 10 unidades · personalización desde 25 · packaging co-branded desde 50 ·
  plazos de 7 a 15 días hábiles · factura A y órdenes de compra · entrega multi-sede.

- **Sin analítica.** No hay ningún script de medición. Si se quiere medir la conversión
  del formulario, el punto natural es un evento en el click de *Enviar por WhatsApp*.

---

## Stack

HTML, CSS y JavaScript sin dependencias. Tipografías **Fraunces** y **Roboto Mono**
desde Google Fonts. Paleta e identidad tomadas del theme del sitio oficial.
