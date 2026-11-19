---
name: motion
description: Diseña, anima y exporta videos con Scenes, Timelines, Vectors, Particles y Export (FFmpeg), dentro de skills de videos. Guía el pipeline Brief → build → animate → refine → render y elige stack (Remotion, Motion Canvas, Three.js, Lottie, Proton, etc.). Úsala al planear escenas, timelines, vectores, partículas o render.
metadata:
  author: pepo
---

# Motion que explica

**Brief → build → animate → refine → render.**

Lee el brief, la voz y las restricciones del proyecto. Antes de programar, define qué debe entenderse, la frase o acción que causa el movimiento y el cuadro de entrada y salida. Si la historia no está clara, resuelve ese punto antes de añadir efectos.

**Scenes. Timelines. Vectors. Particles. Export.**

## La voz manda

La locución se cierra antes de animar en serio y el video se adapta a ella; lo que mejor ha funcionado es que el autor la genere en la web de ElevenLabs y el agente reajuste todo a ese archivo ([voz-elevenlabs](../voz-elevenlabs/SKILL.md)). Cortes, gráficos, subtítulos y efectos se anclan a palabras y se leen de datos, para que un cambio de voz se resuelva regenerando tiempos, no reescribiendo escenas. Anclas, lectura, subtítulos y vertical: [sincronia.md](sincronia.md).

## Pipeline

1. **Brief** — Idea, protagonista, causa de cada transición, énfasis, tiempos de voz reales, estado de entrada/salida y eventos sonoros. No inventes sincronía exacta a partir del texto; con una maqueta estimada solo se boceta.
2. **Build** — Monta la estructura: escenas, capas, assets locales, tipografía y composición. Un protagonista por momento; secundarios sin competir.
3. **Animate** — Aplica timelines, interpolaciones y énfasis solo donde revelen causa, consecuencia, contraste, acumulación o cambio de escala. Reserva el mayor golpe a los descubrimientos.
4. **Refine** — Revisa inicio, momento explicativo y final de cada escena en reproducción continua (no solo capturas). Recorta rebotes, cámara y partículas cuando ya cumplieron su función. Comprueba subtítulos y una sola pista de voz.
5. **Render** — Exporta cuando se solicite. Codifica y muxea con **FFmpeg**; mide audio y revisa el archivo final, no solo la vista previa.

## Capacidades

### Scenes

Unidad narrativa con entrada → acción → salida. Anota idea, objeto protagonista, causa, énfasis, tiempos y eventos sonoros. Compón textos y objetos sin solapes; revisa a tamaño de móvil. Un corte directo puede resolver una transición. Si una captura explica mejor un paso, úsala.

**Stack típico:** Remotion Skills, Motion Canvas, Manim (math), LUME / Three.js / Babylon.js / Godot (3D o game-like), Blender (rigging y personajes).

### Timelines

Secuencias, staggers, tweens y playback con easing. Calcula desde frame + fps cuando el render sea determinista. Evita reloj de pared y `Math.random()` sin semilla. Dentro de una secuencia local, convierte tiempos globales cuando corresponda.

**Stack típico:** Anime.js, Motion (layout), Ola (interpolación suave), Shifty, TweenJS, Remotion (`Sequence`, `interpolate`, `spring`).

### Vectors

Escenas 2D vectoriales, Lottie y canvas interactivo. Recursos locales; registra procedencia y licencias. Si adoptas una técnica de referencia, describe qué adaptaste.

**Stack típico:** Two.js, Lottie Web, Konva, Motion Canvas.

### Particles

Emisores y comportamientos solo si refuerzan la idea (impacto, flujo, disolución). Apágalos en cuanto el espectador ya entendió. Preferir semillas fijas en renders frame-a-frame.

**Stack típico:** Proton; también sistemas de partículas en Three.js, Babylon.js o Godot cuando la escena ya vive ahí.

### Export

Renderiza al pedir entrega. **FFmpeg es el motor de exportación y postproceso**: mux de video/audio, recorte, escala, fps, overlays, GIF y mediciones. No des por cerrado un export sin reproducir y escuchar el archivo.

Flujo habitual:

1. Render del motor de escenas (Remotion, Motion Canvas, Blender, etc.) a frames o video intermedio, sin audio y casi sin pérdida.
2. **FFmpeg** para mux con la mezcla normalizada, loudness (`ebur128`), true peak, escala al formato de plataforma y, si hace falta, GIF con [gifenc](https://github.com/mattdesl/gifenc) o `ffmpeg`/`palettegen`. Revisa rango y matriz de color: Remotion con fotogramas JPEG entrega `yuvj420p` (rango completo, BT.601); detalle en [stack.md](stack.md#ffmpeg-en-export).
3. Verifica el archivo final por script (formato, frames, duración, sonoridad, subtítulos, SHA256) y entrega ruta exacta, comprobaciones y pendientes reales. Nunca sobrescribas una versión ya entregada.

Ejemplos de comprobación (ajusta rutas y preset del proyecto):

```bash
ffmpeg -i video.mp4 -af ebur128=peak=true -f null -
ffprobe -hide_banner -show_format -show_streams video.mp4
```

## Remotion (default cuando el proyecto ya lo usa)

Lee primero la estructura existente y sus comandos. Animación desde `useCurrentFrame()` y fps; `interpolate` / `spring` con extrapolación y duración controladas. `staticFile()` para assets. Guía de agente: [Remotion Skills](https://github.com/remotion-dev/skills). No cambies el stack global solo porque una referencia usa otra librería.

Lo que ha funcionado en proyectos Remotion con voz:

- La duración de la composición sale de los datos de tiempo (`total × fps`), no de una constante.
- Una prop de revisión (`guias`) dibuja zona segura, número de plano y TC; el máster va sin ella y con `--muted`.
- La mezcla entra como un solo `<Audio>`; no dupliques la voz en cada escena.
- Al pedir variantes, copia la versión entregada a `src/vNN/` o a un respaldo antes de tocarla, para poder reproducirla.
- Renders largos en segundo plano. El FFmpeg que trae Remotion es mínimo (sin `ebur128`, `loudnorm`, `xfade`): usa uno completo para mezclar y verificar.

## Elegir herramienta

Elige por el problema visual, no por novedad. Prioriza el stack del proyecto. Catálogo completo y cuándo usar cada una: [stack.md](stack.md).

| Necesitas | Preferir |
|---|---|
| Video React frame-determinista | Remotion + Remotion Skills |
| Explainer procedural / canvas | Motion Canvas |
| Layout / UI motion en web | Motion |
| Stagger / timeline JS | Anime.js, TweenJS, Shifty, Ola |
| Math en movimiento | Manim |
| Vector 2D / Lottie / canvas | Two.js, Lottie Web, Konva |
| 3D en web | Three.js, Babylon.js, LUME |
| Personajes / rig | Blender |
| Game-like / estados | Godot |
| Partículas | Proton (u host 3D) |
| GIF animado | gifenc y/o FFmpeg |
| Mux, codecs, loudness, entrega | **FFmpeg** (siempre en Export) |

## Revisar

Reproduce el tramo completo. Comprueba continuidad, subtítulos y una sola pista de voz. Revisa hojas de contacto cada 0.5 s además de la reproducción continua. Ejecuta los chequeos del proyecto. Tras el export con FFmpeg, informa qué viste, qué escuchaste y qué queda pendiente; si no pudiste escuchar, dilo. Pasar chequeos técnicos no equivale a aprobación editorial.
