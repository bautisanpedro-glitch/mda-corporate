# Material fuente

Lo que hay acá **no se publica**: está listado en `.vercelignore`, así que viaja
al repositorio pero no al deploy. Son 9,4 MB que nadie necesita bajarse entrando
al sitio.

| Archivo | Qué es |
|---|---|
| `caja.mov` | Video original, tal cual salió del teléfono |
| `encode-frames.py` | Elige los frames y los encodea a WebP |

## El video

- 2,63 s · 2160×3840 (4K vertical) · ~74 frames
- Códec **HEVC / H.265** (`hvc1`), contenedor QuickTime

Dos razones por las que el banner no usa este archivo directamente:

1. **HEVC no es confiable en la web.** Chrome y Firefox no lo decodifican salvo
   que el sistema operativo aporte el decoder. En la mayoría de las máquinas no
   se vería nada.
2. **Pesa 9,4 MB.** La secuencia de frames que lo reemplaza pesa 680 KB.

Además, scrubbear un video con el scroll se traba: el navegador tiene que buscar
y decodificar en cada movimiento. Con imágenes precargadas no hay búsqueda.

## Regenerar los frames

Si cambia el video, son dos pasos.

### 1. Extraer los frames

Con ffmpeg instalado, a 540 px de ancho:

```bash
ffmpeg -i caja.mov -vf "scale=540:-2" -q:v 2 frames/g%03d.jpg
```

> El nombre tiene que ser `gNNN.jpg` porque es lo que busca el script del paso 2.

### 2. Elegir y encodear

```bash
python encode-frames.py frames ../box 48 480 72
```

Los argumentos son: carpeta de origen, carpeta de destino, cantidad de frames,
ancho en píxeles y calidad WebP.

El script **no reparte los frames por tiempo sino por movimiento acumulado**:
mide la diferencia entre frames consecutivos y elige los 48 a intervalos iguales
de movimiento. Así el scroll avanza parejo y no se gastan frames en los tramos
donde la caja está quieta.

### 3. Si cambió algo estructural

- Otra cantidad de frames → actualizar la constante `FRAMES` en `index.html`.
- Otra proporción de imagen → ajustar en el CSS el `aspect-ratio`, el `width` y
  `height` del `<canvas>`, y el factor `0.563` (que es ancho ÷ alto del frame).
