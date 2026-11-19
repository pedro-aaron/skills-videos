# Sincronía con la voz

Complemento de [motion](SKILL.md). El video se adapta a la voz cerrada. Ninguna escena fija tiempos a mano si puede leerlos de los tiempos por palabra.

## Una sola fuente de tiempos

- Frases con id y palabras `{w, s, e}` en segundos: `voz-<slug>.frases.json` de [externa.py](../voz-elevenlabs/SKILL.md), las palabras de [voz-whisper](../voz-whisper/SKILL.md) o la respuesta `/with-timestamps` de la API. Un `timeline.json` del proyecto puede reunirlas con la entrada, la cola y el cierre.
- Sin voz todavía, una maqueta reparte el texto a ≈ 15 car/s con pausas cortas en comas y puntos. Márcala como estimada (`"estimada": true`) y no cortes el storyboard final sobre ella.
- Desfase de entrada: los tiempos del archivo cuentan desde su inicio y la composición suma la duración de la cortinilla. La voz entra cuando la identificación de la pieza ya está estable.
- Subtítulos, planos y efectos se derivan de esa fuente. Si cambia la voz: importar → tiempos → subtítulos → storyboard → mezcla → render, sin reescribir escenas. Las escenas leen datos (`planos.json`, `subs.json`, `sfx.json`), no números sueltos.

## Anclar a palabras

- Helpers del tipo `w('p02', 'normas')` → frame de inicio de la palabra (por prefijo normalizado sin acentos, n-ésima aparición), `we()` → fin, `ps()`/`pe()` → inicio de la frase y de la siguiente. Si la palabra no existe, que falle con un mensaje: un cambio de guion no debe romper en silencio.
- Corte de plano 4–6 frames antes de su palabra ancla. Planos de al menos 1.5 s salvo intención; si uno sale más corto, mueve el ancla, nunca la voz.
- Genera el storyboard por script: `planos.json` para las escenas y una tabla legible con ID, TC, frames, ancla, recurso, tratamiento, rótulo, subtítulo y audio. Valida suma exacta de frames, mínimos, solapes y tope de duración.
- Pon un golpe visual en las primeras palabras de cada frase (rótulo, ícono, trazo): tramos de 2–5 s sin cambio se sienten detenidos.
- Precisión: con tiempos de Whisper, una frontera en habla continua puede llegar 0.1–0.3 s antes. Para tipografía palabra a palabra o golpes en sílabas, verifica esas anclas en el espectrograma o al oído.

## Lectura y ritmo

- Cada texto se sostiene lo suficiente para leerse: al menos 1 s para una etiqueta, listas completas desde que aparecen, tarjeta final estable 2–3 s tras la última palabra. Un recuadro que entra en el último medio segundo de un plano no se lee: adelántalo o quítalo.
- Entrada: la pieza se identifica desde el primer segundo. Si el lema debe leerse, dale tiempo aunque alargue la entrada; si eso rompe el tope de duración, decide el autor.
- Un silencio largo en la apertura (≈ 5 s) se siente como interrupción: redistribúyelo hacia el contexto.
- Salida: el mismo motivo de identidad que la entrada, fundido suave y cola negra de 0.2–0.5 s.
- Que una cifra o un dato en pantalla diga lo mismo que la voz en ese momento; si es ilustrativo, el rótulo lo dice.

## Subtítulos desde las palabras

- Una sola fuente (`subs.json`) para los quemados y para el SRT/VTT: mismos cortes y tiempos.
- Bloques de 2 líneas como máximo. En vertical 1080×1920, ≈ 26 caracteres por línea a ≈ 50 px; en 16:9 caben más. Corta tras puntuación; nunca cierres línea ni bloque en palabra funcional («de», «la», «y», «que», «para»…) ni dejes un número colgando.
- El corte de línea lo decide el script (`white-space: pre`), no el navegador: así nunca salen tres líneas.
- Cola de ≈ 0.25 s tras la última palabra, sin solapes (separación ≥ 0.02 s) y dentro de la duración. Evita bloques de una sola palabra.
- Ocúltalos durante remates tipográficos y barridos sin voz; si una palabra empieza dentro del barrido, el subtítulo se queda.
- Comprueba por script: texto de los subtítulos = locución, 0 solapes, primer y último bloque dentro del video. Regenera SRT/VTT cada vez que cambie la voz, sin pisar los de una versión entregada.

## Vertical 9:16 (Reels, Shorts)

- Zona segura aproximada: 260 px arriba, 420 abajo, 130 a los lados y la columna de íconos a la derecha en la mitad inferior. Las guías solo existen en la previsualización.
- Fotos horizontales: recorte vertical con recorrido de cámara (de → a, zoom moderado) que siga los rostros, o panel sobre su copia desenfocada. El zoom crece desde el centro para no destapar bordes; si el recorte deja fuera a una persona, mueve el foco.
- Prepara versiones ampliadas de las fuentes (Lanczos y enfoque leve) en vez de escalarlas en el navegador. Trabaja sobre copias con manifiesto SHA256; los originales no se tocan.

## Revisar

- Previsualización a media escala con guías y TC; hojas de contacto cada 0.5 s (`-vf fps=2`).
- Mira inicio, mitad y final de cada escena y los fotogramas de corte: cuadros vacíos, parpadeos, textos fuera de zona segura, subtítulos en tres líneas, rostros cortados.
- Los chequeos automáticos no reemplazan ver y escuchar el video completo.
