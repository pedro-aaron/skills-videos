# Skills de videos

Un paquete de **pepo**, en español, para pensar, escribir, grabar y animar videos con un agente de IA (Claude Code, OpenCode u otro que lea Markdown). Sirve para cuestionar guiones, preparar voz con Whisper o ElevenLabs y construir animaciones con intención: **Scenes, Timelines, Vectors, Particles, Export** — pipeline **Brief → build → animate → refine → render**, con FFmpeg en la entrega.

**La voz manda.** Lo que mejor ha funcionado en producción: el autor genera la locución en la web de ElevenLabs, la escucha y la descarga; el agente importa ese archivo sin tocarlo, obtiene los tiempos por palabra y adapta el video entero a ella (cortes, gráficos, subtítulos, efectos). Ver [voz-elevenlabs](skills/voz-elevenlabs/SKILL.md).

Salió del taller de videos de pepo. Aquí van las skills y los workflows; no incluye proyectos, grabaciones, música, efectos, modelos ni bibliotecas privadas.

## Contenido

### Skills (`skills/`)

| Skill | Para qué sirve |
|---|---|
| [cuestionar-guion](skills/cuestionar-guion/SKILL.md) | Crítica editorial franca y comparación entre episodios, sin prometer viralidad |
| [voz-whisper](skills/voz-whisper/SKILL.md) | Grabación real: limpieza con FFmpeg, transcripción local con whisper.cpp, cortes de silencios y masterización |
| [voz-elevenlabs](skills/voz-elevenlabs/SKILL.md) | Locución de ElevenLabs: texto etiquetado para la web ([web.md](skills/voz-elevenlabs/web.md)), importación del MP3 descargado sin tocarlo y tiempos por palabra (`externa.py`); TTS por API opcional con voice IDs (`tts.py`, `voces.json`) |
| [referencias-opus](skills/referencias-opus/SKILL.md) | Convertir referencias de catálogos (Awesome Opus u otros) en escenas propias realizables |
| [motion](skills/motion/SKILL.md) | Scenes, Timelines, Vectors, Particles y Export (FFmpeg); [sincronía con la voz](skills/motion/sincronia.md), Remotion por defecto y catálogo en [stack.md](skills/motion/stack.md) |
| [sonido](skills/sonido/SKILL.md) | Efectos, sincronía y mezcla con biblioteca autorizada o síntesis propia; niveles y normalización que han funcionado |

### Content creator (`content-creator/`)

Un espacio de trabajo por módulos: entras por idea, guion, voz, sketchbook visual o producción sin recorrer todas las etapas. Incluye workflows, plantillas de notas y los [criterios editoriales con sus fuentes](content-creator/criterios-de-guion.md). Ver [content-creator/README.md](content-creator/README.md).

## Instalación

**Claude Code:** clona este repositorio como `skills-videos` y copia las carpetas de `skills/` a `~/.claude/skills/` (para todos tus proyectos) o a `.claude/skills/` dentro de tu proyecto. Conserva las subcarpetas; voz-whisper necesita `scripts/voz.py` y voz-elevenlabs necesita `scripts/externa.py`, `scripts/tts.py`, `voces.json` y `web.md`.

```bash
cp -r skills-videos/skills/* ~/.claude/skills/
```

**Otros agentes:** pídele que lea directamente el `SKILL.md` que necesites.

Para el content creator, abre tu agente dentro de `content-creator/`: su `AGENTS.md` explica cómo trabajar.

## Ejemplos

- «Destroza este guion y compáralo con el anterior».
- «Prepara esta toma con voz-whisper; conserva mis pausas cómicas».
- «Prepara el texto con etiquetas para generarlo en ElevenLabs».
- «Aquí está el MP3 que descargué de ElevenLabs: ajusta todo el video a esta voz».
- «Sintetiza una muestra por API con la voz narrador».
- «Adapta una técnica de este enlace al momento en que explico los tokens».
- «Anima esta escena en mi proyecto Remotion».
- «Arma timeline + partículas y exporta con FFmpeg».
- «Mezcla estos efectos debajo de la voz».
- «Rebotemos un guion: traigo esta idea…».

## Voz: requisitos

Python 3 con NumPy, FFmpeg/ffprobe, `whisper-cli` de [whisper.cpp](https://github.com/ggml-org/whisper.cpp) y un modelo GGML multilingüe local. No descarga modelos ni instala nada. La grabación real **no** requiere API keys.

**ElevenLabs desde la web (recomendado):** no requiere API key. `externa.py` necesita Python 3 con NumPy, FFmpeg/ffprobe y un modelo local de transcripción: `faster-whisper` instalado en ese Python con la carpeta del modelo, o `whisper-cli` con un modelo GGML (el mismo de voz-whisper). Tampoco descarga modelos.

**ElevenLabs por API (opcional):** `ELEVENLABS_API_KEY` y voice IDs en [skills/voz-elevenlabs/voces.json](skills/voz-elevenlabs/voces.json) (o una copia del proyecto). Sin clave, la síntesis no corre; usa el camino web o toma + voz-whisper. Muchas claves vienen restringidas a texto a voz (sin forced alignment, transcripción ni lista de voces).

Prepara una carpeta de proyecto con un `video.json` (puede contener `{}`) y pásala con `--project-dir`. El script genera intermedios en `.work/voz`, audio en `public/` y tiempos por palabra en `src/`. La transcripción está configurada para español. El preset requiere escucha y puede necesitar ajustes según la toma. No genera SRT ni incluye un proyecto Remotion.

## Recursos externos

No se incluye el catálogo Awesome Opus, clips de terceros, fuentes, música, efectos ni modelos. Usa recursos cuyos permisos permitan el uso previsto. La licencia de este repositorio no cubre recursos externos.

## Validación

Las skills pasaron un validador de estructura. El script de voz pasó una prueba sintética de entrada, limpieza, detección de silencios, corte, masterización, entrega y rechazo de sobrescritura. Eso no valida la transcripción real con Whisper, la lectura de AUP3, la calidad perceptual, ni llamadas reales a ElevenLabs.

`externa.py` se probó con dos locuciones reales descargadas de la web de ElevenLabs (30 s y 199 s, en español), con faster-whisper small en CPU:

- En la toma larga reprodujo la alineación hecha a mano en esa producción: 98.1 % de coincidencia y los mismos tiempos por palabra (mediana 0 ms), salvo la primera y la última palabra, que ahora se ajustan al nivel del audio. La entrega normalizada midió −16.0 LUFS y −2.7 dBTP, como la original.
- En la toma corta, frente a una alineación DTW independiente, los inicios difieren con mediana de 70 ms y p90 de 200 ms (Whisper adelanta en habla continua; las fronteras con pausa coinciden).
- Se comprobaron el rechazo de sobrescritura, de una segunda locución sin `--reemplazar` y de equivalencias mal escapadas.

No se probaron el motor `whisper-cpp` de `externa.py` ni su uso con otros modelos, y la herramienta no valora cómo suena la voz.

Los criterios añadidos en voz, motion, sonido y producción salen de dos producciones reales con Remotion, ElevenLabs y FFmpeg (un reel vertical de 30–40 s y una presentación horizontal de 3–5 min).

## Relación con el taller

Estas son las versiones genéricas de pepo. El taller de videos de pepo puede llevar en `.claude/skills/` sus propias variantes, atadas a su motor (MOTION.md, asset-vault, `tools/voz.py`). Si mejoras una regla aquí, decide aparte si aplica también allí; no son copias que se sincronicen.

## Licencia

[MIT](LICENSE).
