---
name: voz-elevenlabs
description: Locución con ElevenLabs para video. Camino recomendado, el autor la genera en la web de ElevenLabs y el video se adapta al archivo descargado. El agente prepara y comprueba el texto etiquetado, importa el MP3 sin tocarlo, obtiene tiempos por palabra y entrega voz y palabras. Opcional, síntesis por API con voice IDs del registro local. Úsala al pedir TTS, ElevenLabs, «traigo el audio de ElevenLabs», «ajusta el video a esta voz», preparar el texto para la web, sintetizar narración o elegir una voz por alias o voice_id.
metadata:
  author: pepo
---

# Voz con ElevenLabs: la voz manda

**Audio primero, video después.** Lo que mejor ha funcionado en producción: el autor genera la locución en la web de ElevenLabs, la escucha, elige la toma y la descarga; el agente adapta el video entero (cortes, gráficos, subtítulos, efectos) a ese archivo. La voz no se estira, no se corta ni se reordena para que quepa en el video.

## Por qué la web antes que la API

- El agente no escucha. En la web el autor compara tomas al oído, ajusta etiquetas de emoción y pausa, y regenera solo lo que suena mal.
- Por API, frase por frase, la voz suena cosida. Una toma larga en una sola solicitud metió vocalizaciones espurias en pausas largas («Fu-fu…», palabras inventadas), se aceleró junto a etiquetas densas y leyó ≈ 8 % más rápido que las frases sueltas.
- Las claves de API suelen venir restringidas a texto a voz: sin forced alignment, transcripción, lista de voces ni consulta de créditos (`missing_permissions`). No planifiques sobre esos endpoints sin comprobarlos.
- Las tomas descargadas de la web se alinearon con transcripción local (97–98 % de las palabras con tiempo directo) sin ninguna etiqueta leída en voz alta, y sobre ellas se cerraron las versiones vigentes.

La API sigue disponible (al final) para muestras, pruebas o cuando el autor la pide.

## Camino recomendado: locución desde la web

Detalle de etiquetas, ajustes, problemas vistos y qué devolver al autor: [web.md](web.md).

1. **Guion canónico.** `canonico.txt`, una frase por línea, tal como se verá en pantalla y subtítulos (`id|texto` fija el id). Si el texto es de un cliente, se lee tal cual: compáralo carácter por carácter con el original.
2. **Texto etiquetado.** Lo que el autor pega en la web: las mismas palabras, con etiquetas de dirección (`[con entusiasmo]`, `[pausa]`, `[short pause]`…) y la grafía que ayude a pronunciar. Compruébalo antes de que gaste créditos:

   ```bash
   python3 -I scripts/externa.py guion --guion canonico.txt --etiquetado etiquetado.txt [--equiv equiv.json]
   ```

   Sin etiquetas debe decir lo mismo que el canónico (sale con código 1 si no). Avisa de cifras, mayúsculas, puntos suspensivos y «app», y estima la duración del habla a 13–16 car/s.
3. **El autor genera y elige.** Escucha completo, regenera lo que falle y descarga la toma elegida **sin renombrarla**: el nombre (`ElevenLabs_<fecha>_<voz>_pvc_s50_sim75_v4.mp3`) registra voz, estabilidad y similitud.
4. **Importar sin tocar el audio.** Copia el original con su SHA256, transcribe con un modelo local, empareja cada palabra con el guion y ajusta las fronteras a los silencios medidos:

   ```bash
   python3 -I scripts/externa.py importar mi-video --project-dir /ruta/proyecto \
     --audio "/ruta/ElevenLabs_….mp3" --guion canonico.txt --etiquetado etiquetado.txt \
     --modelo /ruta/faster-whisper-small        # o: --motor whisper-cpp --modelo /ruta/ggml-small.bin
   ```

   Lee `.work/voz/EXTERNA.md`: diferencias entre guion y oído (casi siempre cifras o nombres propios), palabras «añadidas» (posible etiqueta leída o sonido espurio en una pausa), pausas, car/s por frase y sonoridad del original.
5. **Entregar.** `public/voz-<slug>.wav`, `src/voz-<slug>.palabras.json` (mismo formato que voz-whisper) y `src/voz-<slug>.frases.json` (frases con id y palabras en segundos):

   ```bash
   python3 -I scripts/externa.py entregar mi-video --project-dir /ruta/proyecto [--normalizar]
   ```

   `--normalizar` aplica solo una ganancia global en dos pasadas (−16 LUFS / −1.5 dBTP). Sin él, el WAV queda como llegó y la mezcla se normaliza en el export. No sobrescribe sin `--reemplazar`.
6. **Adaptar el video** con [motion](../motion/SKILL.md) y su [sincronía con la voz](../motion/sincronia.md): cortes, gráficos, subtítulos y efectos se recalculan desde los tiempos por palabra.

Requisitos de `externa.py`: Python 3 con NumPy, FFmpeg/ffprobe (o las variables `FFMPEG`/`FFPROBE`) y un modelo local: `faster-whisper` instalado en ese Python con la carpeta del modelo, o `whisper-cli` de whisper.cpp con un modelo GGML (el mismo de voz-whisper). No descarga modelos ni llama a la API.

## Reglas del archivo de voz

- Conserva el original intacto. Nada de cortes, aceleración, reducción de ruido ni compresión dentro de la narración: las pausas son decisión del autor.
- No pases la voz sintética por `limpiar`/`cortar` de voz-whisper: degrada un audio limpio y mueve los tiempos.
- Sin pedirlo solo se permite: ganancia global, desfase de entrada (la voz empieza tras la cortinilla) y relleno al final.
- Un sonido espurio en una pausa se reporta con su tiempo. Silenciarlo es una edición interna: solo con aprobación del autor, sin tocar palabras ni tiempos, y documentada.
- La duración la fija la toma. Si el video queda fuera del rango del encargo, decide el autor: acortar entrada o cierre, recortar texto y generar otra toma, o aceptar la excepción por escrito. No rellenes con silencios ni estires la voz.
- Si cambia la voz, se repite desde el paso 4 y se recalcula todo lo que depende de ella. Montar una voz nueva sobre los tiempos de otra conserva el ritmo y las pausas de la anterior: solo si el autor lo pide sabiéndolo.

## Precisión de los tiempos

Junto a una pausa, la frontera es fiable porque sale del silencio medido. En habla continua, Whisper adelanta las palabras: frente a una alineación independiente, mediana ≈ 70 ms y p90 ≈ 200 ms (máximo ≈ 0.4 s, sobre una toma de 30 s con faster-whisper small). Ajustar las fronteras al valle de energía más cercano o transcribir por tramos no lo mejoró. Alcanza para subtítulos y cortes de plano, que ya van unos frames antes de su palabra. Para tipografía palabra a palabra o un golpe sonoro en una sílaba:

- comprueba esas anclas en el espectrograma o al oído y corrígelas a mano;
- o usa el forced alignment de ElevenLabs si la clave tiene ese permiso;
- o alinea por DTW (MFCC + deltas, tramo por tramo entre pausas) contra una toma de referencia del mismo texto generada con `/with-timestamps`. Fue el método más preciso medido (dos variantes independientes coincidieron con mediana de 10 ms), pero la referencia gasta créditos.

## Registro

En el brief o mapa del proyecto: archivo original y SHA256, voz y ajustes según el nombre, texto etiquetado usado, toma elegida, que la pista es sintética, procesamiento aplicado, coincidencia del ASR y caracteres gastados. Declara siempre que no escuchaste el audio: pronunciación y tono los confirma el autor.

## Camino opcional: API

Solo si el autor lo pide y hay credencial: variable `ELEVENLABS_API_KEY` (o `--api-key`). Nunca la guardes en el repo, en `voces.json` ni en entregables; no la imprimas ni la pidas en el chat. Sin clave, ofrece el camino web, grabar o usar una toma existente. No inventes audio.

### Voice IDs

Orden de resolución: `--voice-id` → `--voz` (alias de [voces.json](voces.json)) → `default`. El `voice_id` es el ID de ElevenLabs (path `/v1/text-to-speech/{voice_id}`), no el nombre comercial. Los ejemplos del registro son plantilla: comprueba IDs reales con `listar` o el dashboard (`listar --remoto` falla si la clave no tiene permiso de voces). Anota en `calibracion` el ritmo medido en un video real: una muestra corta no calibra (15.7 car/s en muestra frente a 14.5 en video con la misma voz).

```bash
python3 -I scripts/tts.py listar
python3 -I scripts/tts.py sintetizar mi-video --project-dir /ruta/proyecto --voz narrador --guion /ruta/guion.txt
python3 -I scripts/tts.py sintetizar mi-video --project-dir /ruta/proyecto --voice-id JBFqnCBsd6RMkjVDRZzb \
  --texto "Frase de prueba." --modelo eleven_multilingual_v2
```

Salida en `.work/voz/`: `00-elevenlabs.mp3` (respuesta cruda), `00-entrada.wav` (mono PCM) y `00-elevenlabs.json` (voz, modelo, caracteres; sin la clave). Para tiempos por palabra, importa el MP3 con `externa.py importar` como si viniera de la web; no lo pases por la limpieza de voz-whisper.

### Lo aprendido con la API

- **Marcado según el modelo.** Multilingual v2: `<break time="0.3s" />`, máximo dos por solicitud y nunca más de 3 s; con más, se acelera o mete ruidos. Las etiquetas entre corchetes y `<phoneme>` no funcionan ahí (se leen o se ignoran): pronunciación escribiendo la palabra como suena en un campo aparte del texto en pantalla.
- **Por frase con contexto.** `previous_text`/`next_text` y semilla fija mantienen la entonación; caché por hash de texto + voz + ajustes para regenerar solo lo que cambió. Los silencios entre frases se insertan al unir, no se le piden al modelo.
- **Tiempos exactos.** `/with-timestamps` devuelve tiempos por carácter; quita los caracteres de las etiquetas antes de agrupar palabras.
- **Ritmo.** Natural entre 13 y 16 car/s (13–15.5 para tono académico); velocidad 0.90–1.10 para corregir. Una toma larga lee ≈ 8 % más rápido que frases sueltas (0.93 lo compensó).
- **Muestras para elegir voz.** Con el texto real completo, igualadas a −18 LUFS para compararlas al oído, con duración y car/s medidos. El nivel de origen varía mucho entre voces (de −12 a −30 LUFS) y hay picos entre muestras de hasta +1.4 dBTP: limitador por pico real en la mezcla.
- **Costo.** Cuenta caracteres antes de generar y registra los gastados; una clave restringida no deja consultar el saldo por API.

## Límites

- Una sola pista de narración por entrega salvo que el brief pida varias.
- Respeta cuotas y términos de ElevenLabs; no redistribuyas voces clonadas sin permiso.
- No reemplaza el criterio editorial ni la sincronía final con motion/FFmpeg. Métricas y ASR no equivalen a escucha.
