# Stack de motion

Catálogo de referencia. Elige según la capacidad (Scenes, Timelines, Vectors, Particles, Export) y el proyecto existente. No instales dependencias nuevas sin que el encargo lo pida.

**Brief → build → animate → refine → render.** Export siempre cierra con **FFmpeg** (mux, codecs, loudness, entrega).

## Catálogo

01 **Remotion Skills** → Agent guidance for video.  
https://github.com/remotion-dev/skills  
Scenes + Timelines en React; frame-determinista. Punto de entrada cuando el proyecto es Remotion.

02 **Motion Canvas** → Animated explainers.  
https://github.com/motion-canvas/motion-canvas  
Scenes procedurales y explainers en canvas/TypeScript.

03 **Motion** → Layout transitions.  
https://github.com/motiondivision/motion  
Transiciones de layout y UI motion en web.

04 **Ola** → Smooth value interpolation.  
https://github.com/franciscop/ola  
Interpolación suave de valores; apoyo a Timelines.

05 **Anime.js** → Timelines and stagger.  
https://github.com/juliangarnier/anime  
Timelines, stagger y secuencias de propiedades.

06 **Manim** → Math in motion.  
https://github.com/ManimCommunity/manim  
Escenas matemáticas; render a video y postproceso con FFmpeg.

07 **Shifty** → Tween playback and easing.  
https://github.com/jeremyckahn/shifty  
Tweens, playback y curvas de easing.

08 **Two.js** → Animated 2D vector scenes.  
https://github.com/jonobr1/two.js  
Scenes vectoriales 2D animadas.

09 **Lottie Web** → Vector animation playback.  
https://github.com/airbnb/lottie-web  
Playback de animación vectorial (After Effects → Lottie).

10 **TweenJS** → Sequenced property animation.  
https://github.com/CreateJS/TweenJS  
Animación secuenciada de propiedades.

11 **LUME** → 3D scenes with HTML.  
https://github.com/lume/lume  
Scenes 3D integradas con HTML.

12 **gifenc** → Animated GIF encoding.  
https://github.com/mattdesl/gifenc  
Codificación de GIF animado; alternativa o complemento a palettegen de FFmpeg.

13 **Konva** → Interactive canvas animation.  
https://github.com/konvajs/konva  
Canvas 2D interactivo y animado.

14 **Blender** → Rigging and character animation.  
https://github.com/blender/blender  
Rigging y personajes; exporta frames/video y termina con FFmpeg.

15 **Three.js** → Animated 3D scenes.  
https://github.com/mrdoob/three.js  
Scenes 3D web; captura/frames + FFmpeg para entrega.

16 **Godot** → Game animation systems.  
https://github.com/godotengine/godot  
Sistemas de animación tipo juego; export y mux con FFmpeg si hace falta entrega de video.

17 **Babylon.js** → 3D animation and rendering.  
https://github.com/BabylonJS/Babylon.js  
Animación y render 3D en web.

18 **Proton** → Particle emitters and behaviors.  
https://github.com/drawcall/Proton  
Emisores y comportamientos de partículas.

## Por capacidad

| Capacidad | Herramientas |
|---|---|
| **Scenes** | Remotion Skills, Motion Canvas, Manim, LUME, Three.js, Babylon.js, Godot, Blender |
| **Timelines** | Anime.js, Motion, Ola, Shifty, TweenJS, Remotion |
| **Vectors** | Two.js, Lottie Web, Konva, Motion Canvas |
| **Particles** | Proton; también Three.js / Babylon.js / Godot si la escena ya es 3D |
| **Export** | **FFmpeg** (obligatorio para mux, codecs, loudness, recorte, escala); gifenc para GIF; Remotion/Motion Canvas/Blender/Manim como render de escenas |

## FFmpeg en Export

Usa FFmpeg en el cierre del pipeline, no como sustituto del diseño de escenas:

- Mux de video renderizado + voz masterizada
- Recorte, escala, fps y formato de plataforma
- GIF (`palettegen`/`paletteuse`) o frames → gifenc
- Medición: `ebur128`, true peak; inspección con `ffprobe`

Respeta presets y rutas del proyecto. No inventes codecs ni bitrates “oficiales” de plataforma sin que el brief o el proyecto los fijen.

### Entrega desde Remotion (probado)

- **Color.** Con fotogramas JPEG, Remotion entrega `yuvj420p`: rango completo y matriz BT.601. Las plataformas esperan `yuv420p` de rango estándar. Dos caminos que funcionaron:
  - render con `--image-format=png --pixel-format=yuv420p --color-space=bt709`;
  - o render mudo con `--crf=16` y conversión al final: `-vf scale=in_range=pc:out_range=tv:in_color_matrix=bt601:out_color_matrix=bt709,format=yuv420p -c:v libx264 -preset slow -crf 15 -profile:v high -color_range tv -colorspace bt709 -color_primaries bt709 -color_trc bt709`.

  Comprueba un color de marca decodificado contra el original (una diferencia de 1–3 en cada canal es normal).
- **Mux.** Video del render mudo (`-c:v copy` si ya es `yuv420p`) + mezcla normalizada a AAC 48 kHz 192 kb/s, `-movflags +faststart` y `-t` con la duración exacta del timeline.
- **FFmpeg completo.** El que trae Remotion no tiene `ebur128`, `loudnorm`, `xfade` ni filtros como `fps`/`select`: mezcla, verifica y extrae fotogramas con un FFmpeg completo.
- **Verificación por script** que deje un JSON y un README: contenedor con `moov` al inicio, H.264 `yuv420p`, resolución, fps, número de frames = duración × fps, duración dentro del rango del encargo, AAC 48 kHz, sonoridad y pico real del archivo final, subtítulos = locución sin solapes y dentro del video, SHA256 de cada entregable. Si una excepción fue autorizada (por ejemplo, pasar del tope de duración), el script la refleja en vez de ocultarla.
