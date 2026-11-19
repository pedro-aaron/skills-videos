# Sketchbook visual en el chat

Es una conversación para diseñar lo que se ve y cómo se desarrolla. Puede empezar antes de grabar, con voz terminada, con una referencia o con una corrección. No exige Docker ni código de animación para comenzar.

## La ronda

1. Recupera la frase o intención de una secuencia. Devuelve qué entiendes en una o dos frases, conservando el lenguaje del autor.
2. Propón dos caminos cuando exista una decisión real; hasta tres si son útiles. Deben diferir en cómo cuentan la idea, no solo en paleta. Recomienda uno y explica el intercambio.
3. El autor puede elegir, mezclar o corregir en lenguaje natural. «B, sin explosión» ya decide; no pedir confirmación redundante.
4. Desarrolla la ruta elegida en pocos cuadros clave: entrada, cambio y resultado suelen bastar. Añade anticipación o remate solo si aportan.
5. Muestra el boceto aquí y conversa sobre esa secuencia. Al cerrar la ronda, guarda qué quedó, qué sigue abierto y el siguiente paso.

No hagas que el autor rellene todos los campos antes de poder pensar. Si falta una decisión esencial, pregunta una cosa por vez y avanza en lo independiente.

## Lo que concretamos por secuencia

- Frase de voz o intención; tiempo aproximado si existe.
- Qué debe entenderse y qué aporta la imagen frente a lo dicho.
- Cuadros clave: encuadre, foco, texto exacto y relación entre objetos.
- Qué cambia, qué permanece y dónde hace falta leer o esperar.
- Entrada y salida: corte, continuidad, aparición, comparación, transformación u otro recurso con función clara.
- Recursos reales, metáfora o recreación; identificar cuál es cuál.
- Relación con lo anterior y siguiente, si se conocen.

Antes de animar, acordar lo necesario de tipografía, roles del color, materialidad, encuadres y subtítulos. Usar las decisiones vigentes de la pieza; las referencias históricas no obligan a recuperar un fondo descartado o poner rostro en todo.

## Verlo aquí mismo

Un boceto textual rápido sirve para distribuir elementos. Cuando la decisión depende del aspecto, generar y mostrar cuadros visuales quietos con texto real: esquemas SVG/HTML para composición o imágenes cuando el material lo requiera. Guardar los bocetos junto al sketchbook y mostrarlos con las herramientas de imagen disponibles; no limitar la revisión a pedir que el autor imagine párrafos. Si el entorno no permite mostrar una imagen, explicar el límite y entregar el esquema/archivo disponible.

Distinguir wireframe, cuadro de estilo y captura de implementación. Un boceto aprobado fija una intención; no certifica legibilidad temporal ni render final. Primero resolver composición; después el animatic con voz comprueba duración y relaciones.

«Cada frame» empieza por cuadros clave. A 30 fps, describir 300 fichas de una escena de diez segundos no ayuda a decidir. Una vez fijada la voz, ubicar eventos importantes en segundos y frames para implementarlos. Si el autor pide un fotograma concreto, sí revisarlo a esa precisión.

## Ejemplo ficticio de una ronda

Frase: «Le pido mover un cuadrito y cambia todo lo demás».

- A: comparación de petición y resultado con material real, si existe.
- B: el cuadrito permanece quieto mientras cambia todo alrededor; recreación gráfica identificada.

Si elige B, desarrollar:

| Cuadro | Qué vemos | Qué entiende alguien |
|---|---|---|
| Entrada | Composición estable, selección sobre un solo cuadrito | El pedido tiene alcance pequeño |
| Cambio | Fondo, texto y posiciones vecinas cambian; el cuadrito permanece | La respuesta excede lo pedido |
| Resultado | Mantener visible el cuadrito en su posición original | El contraste entrega el chiste |

Este ejemplo no es una escena elegida ni una experiencia nueva atribuida al autor. Los tiempos y materiales siguen abiertos.

## Decisiones y paso a producción

Guardar un resumen pequeño: secuencia, elegido, conservar, pendiente y siguiente. Mantener alternativas descartadas solo cuando ayuden a no repetirlas. No dar por aprobada una ruta que el agente propuso pero el autor no eligió.

«Me gusta la composición» cierra composición. «Anima esta secuencia» autoriza esa implementación. Una petición inicial que ya incluya producción conserva su autorización; no exigir aprobación por cada movimiento de detalle. Agrupar las decisiones que sí cambian el rumbo.

Al pasar a producción, registrar lo acordado en el contrato de motion del proyecto. Resolver diferencias con reglas heredadas mediante las elecciones explícitas del autor, sin modificar candados técnicos. Si cambia voz o alcance, reabrir solo las secuencias dependientes.
