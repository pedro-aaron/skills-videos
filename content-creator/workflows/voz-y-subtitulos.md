# Voz y subtítulos

Entrada: una grabación, **o** una locución de ElevenLabs, y una carpeta de proyecto acordada. Conserva siempre el original y no instales ni descargues herramientas por defecto.

**La voz manda:** se cierra antes de animar y el video se adapta a ella. Con una locución sintética, lo que mejor ha funcionado es que el autor la genere en la web de ElevenLabs y el agente reajuste el video a ese archivo.

## Elegir el alcance

- **Locución desde la web de ElevenLabs (recomendado para voz sintética):** sigue [voz-elevenlabs](../../skills/voz-elevenlabs/SKILL.md). El agente prepara el guion canónico y el texto etiquetado y los comprueba con `externa.py guion`; el autor genera, escucha y descarga la toma sin renombrarla; el agente la importa sin tocar el audio (`externa.py importar`), revisa `EXTERNA.md` y entrega voz y palabras (`externa.py entregar`). No pasa por la limpieza ni por los cortes de voz-whisper.
- **TTS por API (opcional):** con `ELEVENLABS_API_KEY` y un alias/`voice_id` de [voces.json](../../skills/voz-elevenlabs/voces.json), `tts.py sintetizar` y después `externa.py importar` sobre el MP3 generado. Sin clave, no llames la API: ofrece el camino web, grabar o usar una toma existente.
- **Solo limpiar (grabación real):** `entrada` y `limpiar` de [voz-whisper](../../skills/voz-whisper/SKILL.md); comparar a volumen parecido y entregar `01-eq.wav`. Sin cortes ni transcripción.
- **Voz completa (grabación real):** la cadena por etapas de voz-whisper, revisando la transcripción antes de cortar. Conserva pausas expresivas: las del humor no son material sobrante.
- **Solo subtítulos:** partir de la voz vigente y sus palabras; no reprocesar el audio.

La petición del autor determina el alcance; no pedir que elija un modo si ya quedó claro.

## Duración

La toma fija la duración. Estima antes de generar (caracteres ÷ 14.5 car/s + entrada + cierre) y mide después. Si queda fuera del rango del encargo, el autor decide entre acortar entrada o cierre, recortar texto y generar otra toma, o aceptar la excepción por escrito. No se rellena con silencios ni se estira la voz.

## Subtítulos

Los scripts entregan tiempos por palabra: **no generan SRT, agrupación de frases ni diseño visual**. Decide el entregable (SRT/VTT, subtítulos en el video o ambos). Reglas detalladas en [sincronía con la voz](../../skills/motion/sincronia.md#subtítulos-desde-las-palabras).

1. Partir de la voz vigente y sus palabras revisadas; registrar la versión de audio usada.
2. Agrupar por sentido y lectura: máximo 2 líneas (≈ 26 caracteres por línea en vertical 1080×1920), cortes tras puntuación, nunca terminar línea ni bloque en «de», «la», «y», «que»… El texto de los subtítulos es el canónico, no lo que escribió el ASR.
3. Para SRT/VTT: tiempos positivos, ordenados, sin solapes (cola de ≈ 0.25 s y separación ≥ 0.02 s) y dentro de la duración. Una sola fuente para los quemados y el archivo.
4. Elegir encuadre y estilo en el sketchbook; no animar cada palabra por defecto. Ocultarlos durante remates tipográficos y barridos sin voz.
5. Revisar con la voz y en tamaño de teléfono. Si cambia la voz, regenerar sin pisar los archivos de una versión ya entregada.

Salida: rutas de voz, palabras y subtítulos generados; qué se escuchó, qué solo se midió y qué queda pendiente.
