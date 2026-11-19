# Producir una pieza

Para implementar secuencias ya elegidas en tu proyecto de video. No reconstruye las etapas anteriores.

Pipeline de motion: **Brief → build → animate → refine → render.** Capacidades: **Scenes. Timelines. Vectors. Particles. Export.**

**La voz manda.** La locución se cierra antes de animar en serio y el video se adapta a ella. Con voz sintética, lo que mejor ha funcionado es que el autor la genere en la web de ElevenLabs y el agente reajuste todo a ese archivo ([voz-elevenlabs](../../skills/voz-elevenlabs/SKILL.md)). Sobre tiempos estimados se puede bocetar, pero el storyboard final y los cortes salen de la voz medida.

1. **Proyecto.** Acuerda cuál es y lee sus instrucciones, brief y configuración antes de editar. Completa intención, público, guion, duración/formato y criterio de aprobación. Si el texto es de un cliente, es fijo: compáralo carácter por carácter con el original.
2. **Voz y tiempos.** Importa la voz vigente y obtén sus tiempos por palabra ([voz y subtítulos](voz-y-subtitulos.md)). Compara la duración real con la del encargo; si no cabe, decide el autor.
3. **Contrato de motion.** Lee la skill [motion](../../skills/motion/SKILL.md), su [sincronía con la voz](../../skills/motion/sincronia.md) y, si hace falta elegir herramienta, [stack.md](../../skills/motion/stack.md). Anota en el brief, por escena: qué debe entenderse, palabra ancla y causa de cada movimiento, estados de entrada/salida, timelines y si hay vectores o partículas, partiendo del sketchbook. Genera el storyboard sobre la voz medida.
4. **Build + Animate.** Arranca la vista previa del proyecto (p. ej. Remotion Studio) y comparte la URL real. Animación por frame cuando el motor lo permita; recursos locales; sin reloj ni aleatoriedad sin semilla. Primero cuadros clave; luego secuencia continua con voz. Tiempos leídos de datos, no escritos a mano.
5. **Sonido.** Con imagen estable, sigue la skill [sonido](../../skills/sonido/SKILL.md). Documenta archivos, procedencia y licencia (o que es síntesis propia).
6. **Refine + Export.** Ejecuta los chequeos del proyecto; revisa inicio, mitad y final en tamaño de teléfono y hojas de contacto. Renderiza solo cuando se pida. **Cierra con FFmpeg**: mux de video + mezcla, escala/formato y color, medición de loudness; GIF con gifenc o FFmpeg si el encargo lo pide. Reproduce y escucha el archivo final. Entrega ruta exacta, comprobaciones y pendientes reales. Cierra la vista previa que abriste.

Pasar chequeos técnicos no equivale a aprobación: la aprueba quien ve y escucha el video. Si no pudiste escuchar, dilo en la entrega.

## Estructura que ha funcionado

```text
<pieza>/
├── fuente/        copias de los insumos (originales intactos) + manifiesto con SHA256
├── proyecto/      código del video (p. ej. Remotion) y script/ con guion y datos
├── intermedios/   voz, renders de revisión, hojas de contacto, logs
└── entregables/   MP4, SRT/VTT, textos y README de verificación
```

- Un mapa vivo del proyecto (estado, decisiones, pendientes y registro fechado) que se actualiza al cerrar cada sesión. Quien retome lee primero ese mapa.
- Insumos del cliente: no se modifican; se trabaja sobre copias.
- Decisiones del autor numeradas (D1, D2…) y fechadas; una propuesta del agente no es una decisión.
- Créditos de TTS gastados y voces probadas, anotados con su ritmo medido.
- Si un mismo tipo de pieza se repite, conviene un prompt maestro por etapas y una tabla de frases que lo disparan; no hace falta para una pieza aislada.

## Entrega y versiones

- Cada entrega lleva sufijo de versión (`_v2`). La anterior se archiva completa (`entregables/v1_<fecha>/`) con sus hashes y no se sobrescribe. Ojo con las herramientas que escriben directo en entregables: un script que regenera el SRT puede pisar el de la versión entregada.
- Antes de rehacer, respalda datos y escenas de la versión entregada para poder reproducirla.
- README de entregables: archivos, ficha (duración, voz y cómo se generó, música, imágenes, tipografía), cambios frente a la versión anterior, decisiones tomadas por defecto, tabla de verificación y SHA256. Nunca incluyas claves ni el `.env`.
- Verificación mínima del MP4 (ajusta al encargo): `moov` al inicio (`+faststart`), H.264 `yuv420p`, resolución y fps, frames = duración × fps, duración en el rango pedido (o excepción autorizada y anotada), AAC 48 kHz, sonoridad y pico real del archivo final, subtítulos = locución, sin solapes y dentro del video.
