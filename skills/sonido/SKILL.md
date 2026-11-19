---
name: sonido
description: Selecciona efectos de una biblioteca local y ajusta mezcla y sincronía para videos. Úsala para diseñar golpes, transiciones, ambientes o música bajo voz; requiere recursos propios o con permiso de uso.
metadata:
  author: pepo
---

# Sonido con intención

Identifica el video, fps, duración y biblioteca disponible. Esta skill no incluye audios. Usa la biblioteca autorizada del usuario y respeta las reglas del proyecto sobre su origen (por ejemplo, una carpeta o script obligatorio). No inventes rutas ni presupongas que existe un script.

1. Fija primero eventos visuales y narrativos. Elige efectos por causa perceptible o intención narrativa; evita ruido por cada palabra. Un ambiente continuo puede ser intencional.
2. Busca candidatos en el catálogo disponible. Nombres y etiquetas no prueban cómo suenan: preescucha antes de elegir. Si no puedes escuchar, presenta la selección como provisional.
3. Copia solo los recursos usados a la carpeta del proyecto. Conserva la biblioteca original y documenta origen, licencia y cambios. No redistribuyas packs comprados por el hecho de tenerlos localmente.
4. Alinea el ataque o pico del efecto con el impacto, no necesariamente el inicio del archivo. Calcula inicio = cuadro del impacto / fps − tiempo del pico. Si resulta negativo, ajusta el montaje o recorta una copia sin destruir el original. Respeta las colas y evita clics de corte.
5. Mantén inteligible la voz; automatiza música y efectos en remates y pausas. Mide el conjunto, no solo pistas aisladas. En Remotion evita duplicar voz o montar un efecto fuera de su duración.
6. Reproduce y mide el export final. Con FFmpeg, `ffmpeg -i video.mp4 -af ebur128=peak=true -f null -` permite leer LUFS y true peak. Usa el objetivo del proyecto; si falta, propone uno como criterio de trabajo, no regla universal de plataforma. Un pico correcto no garantiza mezcla agradable.

Entrega archivos usados, eventos de sincronía, mediciones y pendientes reales. No afirmes haber escuchado si solo analizaste métricas. Descargar o generar nuevos recursos requiere que esté dentro del encargo; prioriza lo existente.

## Sin biblioteca: síntesis propia

Si no hay biblioteca autorizada o el tema pide sobriedad, la cama y los efectos pueden sintetizarse por código (NumPy/SciPy): colchón cálido y bajo sin percusión para temas serios; tics, barridos, campanas suaves, golpes graves o un acorde de arranque para la entrada. Es material original sin licencias de terceros: documéntalo como síntesis. Cachea lo que tarde en generarse. Si piden un sonido «tipo» de una marca, resuélvelo con uno propio, no con una imitación reconocible.

## Niveles que han funcionado

Son criterios de trabajo, no reglas de plataforma; el objetivo del proyecto manda.

- Voz a ≈ −18 dBFS RMS. Música unos 10 dB por debajo mientras se habla en piezas educativas o comerciales, y unos 18 dB en temas serios; sube 4–6 dB en pausas largas y en una entrada sin voz, para que no quede en silencio.
- Ducking con filtros de mínimo y promedio móvil (`scipy.ndimage.minimum_filter1d`, `uniform_filter1d`). `np.convolve` sobre la señal completa se cuelga.
- Efectos sutiles (≈ −18 a −20 dB) anclados a palabras o a frames en un archivo de datos (`sfx.json`: frase + palabra o tiempo absoluto), para que sigan a la voz si cambia.
- Limitador por pico real (sobremuestreo ×4): las voces de ElevenLabs traen picos entre muestras de hasta +1.4 dBTP aunque el pico de muestra parezca seguro.
- Normalización final con `loudnorm` en dos pasadas a −16 LUFS / −1.5 dBTP (LRA 11, `linear=true`) y AAC a 48 kHz. Si el LRA medido supera el objetivo (entrada y cierre sin voz), FFmpeg cambia a modo dinámico: anótalo.
- Para comprobar que cada palabra tiene energía en la mezcla final, tolera ±60 ms por el retardo del codificador AAC (≈ 42 ms), y que en las pausas de la locución no aparezcan sonidos de voz.
