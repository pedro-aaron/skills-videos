# Locución desde la web de ElevenLabs

Guía del camino recomendado de [voz-elevenlabs](SKILL.md): qué prepara el agente, qué hace el autor en la web y qué se devuelve. Lo observado aquí salió de producciones reales en español (un reel vertical de 30–40 s y una presentación de 3–5 min); no es una garantía del servicio.

## Lo que prepara el agente

- `canonico.txt`: una frase por línea, como se verá en pantalla. `id|texto` fija ids estables (por ejemplo `p43b|…` para una frase insertada sin renumerar las demás).
- `etiquetado.txt`: el texto para pegar en la web.
- `equiv.json` (opcional): equivalencias para el emparejamiento, aplicadas a cada palabra en minúsculas y sin acentos, tanto del guion como de lo que oye el ASR: `{"\\b2026\\b": "dos mil veintiseis", "%": " por ciento"}`. En JSON la barra de las regex va doble; con una sola, `\b` es un retroceso y `externa.py` lo rechaza.
- La duración prevista: caracteres ÷ ritmo (14.5 car/s es un buen punto medio; 13–16 es el rango natural) + entrada + cierre. Con texto fijo y tope de duración, mide el riesgo antes de que el autor genere.

## Escribir el texto etiquetado

- Mismas palabras que el canónico. La puntuación sí puede cambiar para guiar la entonación.
- Etiquetas entre corchetes para dirección y pausas. Son de los modelos con etiquetas de audio de la web (Eleven v3 en adelante); en Multilingual v2 se leen o se ignoran y ahí se usa `<break time="0.5s" />`. No mezcles los dos marcados.
- Una etiqueta de tono al empezar cada bloque o cambio de intención basta. `[pausa]` entre ideas o bloques, `[short pause]` dentro de una frase; dos `[pausa]` seguidas alargan el silencio.
- Etiquetas usadas sin que se leyeran en voz alta: `[con entusiasmo]`, `[pausa]` y `[short pause]` en un reel institucional; `[professional]`, `[thoughtful]`, `[confident]`, `[clear]`, `[steady]`, `[emphatic]`, `[informative]`, `[calm]`, `[urgent]` y las dos de pausa en una presentación comercial. Mezclar etiquetas en español y en inglés funcionó.
- Pronunciación: el canónico conserva la grafía (marcas, siglas, cifras). El etiquetado puede escribir cómo se dice («artículo cuatro», «Ai strákcher») y `equiv.json` declara la correspondencia. Evita «app» (se oyó «AP»): «aplicación». Las mayúsculas sostenidas pueden deletrearse. Sin puntos suspensivos ni rayas.
- Nombres propios y marcas: revísalos todos juntos al oído. El ASR puede escribir mal un nombre bien pronunciado; eso no prueba un error de la voz.

`externa.py guion` comprueba que, sin etiquetas, el texto diga lo mismo que el canónico, y avisa de lo anterior.

## En la web (lo hace el autor)

- Voz elegida: clon (PVC/IVC) o de la biblioteca. Ajustes de partida que funcionaron: estabilidad 0.50, similitud 0.75.
- Generar, escuchar completo y regenerar lo que falle. En tomas largas, revisar sobre todo las pausas largas (ahí aparecieron sonidos espurios en otras pruebas) y que no se acelere junto a etiquetas.
- Descargar la toma elegida **sin renombrarla** y decir cuál es si hay varias. El nombre trae fecha, voz, tipo de clon, estabilidad y similitud (`…_pvc_s50_sim75_v4.mp3`); el sufijo final parece indicar el modelo, sin verificar.

## Lo que devuelve el agente

Tras `externa.py importar`: coincidencia del ASR, diferencias, posibles etiquetas leídas, pausas, ritmo por frase y duración del habla; con eso, la duración proyectada del video. Tras `entregar` y el reajuste del video: qué cambió, qué se verificó y que no escuchó el audio.

## Problemas vistos y qué hacer

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| Palabra «añadida» dentro de una pausa | Sonido espurio o etiqueta leída | Escuchar el tramo; otra toma, o silenciar solo ese hueco con aprobación del autor |
| Cifras, siglas o marcas como «cambio» | Reconocimiento del ASR | Declarar `equiv.json` o ignorar si se oye bien; no es error del audio |
| Un tramo a más de 16 car/s | Etiquetas densas o tramo largo sin pausas | Menos etiquetas, partir la frase o bajar la velocidad en la web |
| La toma excede la duración del encargo | Texto largo o pausas largas | Decide el autor: entrada o cierre más cortos, texto más corto con otra toma, o excepción documentada |
| Coincidencia baja (< 90 %) | Otro archivo, otro texto o etiquetas leídas | Confirmar que archivo y guion son los vigentes antes de seguir |
| La primera palabra empieza en 0.0 s | Toma sin silencio inicial | Normal; el desfase de entrada lo pone la composición |
