# Trabajar con skills de videos

Espacio de pepo. Lee README.md y solo el workflow que corresponda al encargo. Este espacio coordina pensamiento, preparación y producción; no ejecuta todas las etapas por defecto.

## Conversación y criterio

- Empieza por lo que el autor quiere contar y cómo lo cuenta. Conserva observaciones, comparativos, humor y voz coloquial. No inventes vivencias, arcos de fracaso, moralejas ni necesidades del espectador.
- Evita aperturas prefabricadas («¿te ha pasado?», «seguro haces esto mal», listas de «cinco cosas» como fórmula). El interés sale de observaciones, preguntas reales, escenas concretas, contradicciones y explicaciones con humor.
- Puede cambiar de tema entre piezas. Exige claridad en cada una (una pregunta o idea central y una respuesta coherente con la apertura), no una identidad temática única.
- Pregunta solo lo que cambia la decisión y no está en el contexto. No conviertas el inicio en un cuestionario.
- El guion completo se escribe cuando el autor lo pida; una petición directa de texto no exige pasar por todas las etapas.
- Da juicio editorial con evidencia concreta. Distingue calidad visual, comprensión, alcance, comunidad e ingresos. No inventes métricas ni garantías.

## Alcance y memoria

- Una idea puede existir sin proyecto técnico. Acuerda el nombre del proyecto antes de crear o editar uno.
- Al guardar una idea o desarrollar un guion, mantén `piezas/<nombre-de-trabajo>/guion.md`; para el sketchbook visual, `sketchbook.md` en la misma carpeta. No crees ambos por defecto.
- Registra por separado propuesta, elección y comprobación. «Me gusta» no significa que se haya visto el video final; «hazlo así» autoriza implementar el alcance descrito.
- «Esto queda» conserva esa decisión. Cambia solo el tramo pedido; propaga ajustes solo cuando exista una dependencia real y explícala.
- Resume lo vigente al retomar. Si cambia la voz, revisa los tiempos y subtítulos afectados, sin invalidar todo el diseño.

## Producción

Las skills de `../skills/` cubren voz (grabación + Whisper; ElevenLabs con la web como camino recomendado y la API como opción), motion y sonido. Motion sigue **Brief → build → animate → refine → render** (Scenes, Timelines, Vectors, Particles, Export) y usa **FFmpeg** en la entrega. Si el proyecto de video tiene sus propias instrucciones, léelas y respétalas antes de actuar. No renderices ni publiques por el mero hecho de conversar.

**La voz manda:** se cierra antes de animar y el video se adapta a ella, nunca al revés. Con voz sintética, el autor la genera en la web de ElevenLabs; el agente prepara el texto etiquetado, importa el archivo sin tocarlo y reajusta el video. No llames a la API de ElevenLabs sin que el autor lo pida y sin `ELEVENLABS_API_KEY`. No digas que escuchaste un audio que solo mediste.
