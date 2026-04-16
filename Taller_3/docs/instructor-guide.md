# Guia del docente — Taller 3: De MapReduce a Spark

## Objetivo

Hacer tangible la transicion de MapReduce a Spark. Al terminar la sesion, los estudiantes deben poder explicar con sus propias palabras por que Spark desplazo a MapReduce, no solo saber que lo desplazo.

## Pre-requisito

Haber completado el Taller 2. Los estudiantes deben saber:
- Que es HDFS y como se organiza en NameNode + DataNodes.
- Que son los pares clave-valor en MapReduce.
- Como ver un job en YARN UI (puerto 8088).
- Como interpretar el resultado de un wordcount en HDFS.

Si algun grupo no completo el Taller 2, puede ejecutar `make hdfs-init` para cargar los datos y luego proceder directamente al Lab 2.

## Agenda sugerida (2.5 horas)

| Bloque | Duracion | Actividad |
|--------|----------|-----------|
| 1 | 15 min | Repaso de MapReduce y motivacion para Spark |
| 2 | 20 min | Levantar el cluster extendido (`make up`, `make ps`) |
| 3 | 25 min | Ejecutar `make wordcount-mr` y analizar en YARN UI |
| 4 | 25 min | Ejecutar `make wordcount-spark` y analizar en Spark UI |
| 5 | 15 min | `make compare` y discutir la tabla de tiempos |
| 6 | 20 min | Analizar diferencias de codigo (MR Java vs PySpark) |
| 7 | 10 min | Intro a lo que viene en el Taller 4 |

## Bloque 1: Repaso y motivacion (15 min)

Preguntar: ¿que problemas vieron en MapReduce el taller anterior? Guiar hacia:
- Verbosidad del codigo Java (Mapper, Reducer, Driver).
- Tiempo de ejecucion para un dataset pequeño.
- Escritura en disco en cada etapa.

Introducir Spark como respuesta a esas limitaciones. No dar la explicacion completa todavia: dejar que emerja de la ejecucion.

## Bloque 2: Levantar el cluster (20 min)

```bash
make up     # arranca los 10 contenedores
make ps     # verificar que todos esten Running
```

Pedir a los estudiantes que cuenten los servicios: 7 de Hadoop + 3 de Spark = 10 en total.

Abrir las cuatro interfaces y dejar que naveguen brevemente:
- `http://localhost:9870` — NameNode (ya conocido del Taller 2)
- `http://localhost:8088` — ResourceManager (ya conocido)
- `http://localhost:19888` — JobHistory (ya conocido)
- `http://localhost:8080` — Spark Master UI (nuevo)

En Spark UI mostrar: los dos workers registrados, la memoria y cores disponibles.

## Bloque 3: WordCount con MapReduce (25 min)

```bash
make hdfs-init      # carga los 4 archivos .txt en HDFS
make wordcount-mr   # ejecuta el job y muestra el tiempo
```

Mientras corre, abrir YARN UI y mostrar el job en ejecucion. Al terminar, ir a JobHistory y mostrar:
- Cuantos mappers se ejecutaron.
- Cuantos reducers.
- El tiempo total del job.
- Los contadores de bytes leidos y escritos en disco.

Anotar el tiempo en la pizarra.

## Bloque 4: WordCount con Spark (25 min)

```bash
make wordcount-spark   # ejecuta el job PySpark y muestra el tiempo
```

Mientras corre, abrir Spark UI (`http://localhost:8080`) y navegar a la aplicacion activa. Mostrar:
- El DAG con los stages.
- Cuantos tasks hay por stage.
- El tiempo de cada stage.

Al terminar, anotar el tiempo en la pizarra junto al tiempo de MapReduce.

## Bloque 5: Comparacion de tiempos (15 min)

```bash
make compare   # ejecuta ambos en secuencia y muestra la tabla
```

Discutir los numeros. Puntos clave:

- Con un dataset de pocos kilobytes la diferencia puede ser modesta o incluso Spark puede tardar mas en el primer run (por el overhead de inicializacion de la JVM y la conexion al master).
- Eso no invalida la superioridad de Spark: el overhead es fijo, el beneficio escala con los datos.
- Con gigabytes de datos o con algoritmos iterativos (ML), Spark puede ser 10x-100x mas rapido.

Preguntar: ¿que pasaria si corremos el mismo job 10 veces seguidas? En Spark, las particiones pueden quedar en cache; en MapReduce, siempre se lee desde HDFS.

## Bloque 6: Comparacion de codigo (20 min)

Abrir el archivo `jobs/wordcount.py` y leerlo en voz alta. Contarlo: menos de 15 lineas de logica real.

Contrastar con el WordCount.java del ecosistema Hadoop:
- Clase `TokenizerMapper` con `map()`.
- Clase `IntSumReducer` con `reduce()`.
- Clase `WordCount` con el metodo `main()` y la configuracion del job.
- Total: ~60 lineas sin contar imports.

Preguntar: ¿que abstraccion usa Spark en lugar de Mapper y Reducer? (RDDs con transformaciones funcionales: `flatMap`, `map`, `reduceByKey`).

Mostrar la equivalencia conceptual:
- `flatMap` = Mapper (una linea → muchos pares).
- `reduceByKey` = Reducer (muchos pares → un valor por clave).
- `sortBy` = no tiene equivalente directo en MapReduce basico; necesitaria un segundo job.

## Bloque 7: Intro al Taller 4 (10 min)

El Taller 4 usa Spark con DataFrames en lugar de RDDs, y Parquet en lugar de archivos de texto.

Preguntar: ¿que limitacion tiene este wordcount en Spark? (Usa RDDs de bajo nivel; no aprovecha el optimizador de consultas Catalyst de Spark SQL).

Anticipar: DataFrames son como tablas SQL sobre datos distribuidos. Parquet es un formato columnar que permite leer solo las columnas necesarias. El Taller 4 mostrara como esas dos ideas juntas dan otro salto de eficiencia.

## Conceptos a enfatizar durante toda la sesion

**DAG vs fases discretas**: MapReduce tiene exactamente tres fases (Map, Shuffle, Reduce) por job. Spark construye un grafo dirigido aciclico de operaciones y lo optimiza antes de ejecutar. Eso permite fusionar operaciones que en MapReduce requererian jobs separados.

**Shuffle en memoria vs disco**: el cuello de botella de MapReduce es que el shuffle escribe en disco local y luego transfiere por red. Spark hace el shuffle en memoria cuando es posible y solo spills a disco si no hay suficiente RAM.

**Lazy evaluation**: Spark no ejecuta nada hasta que se llama una accion (`saveAsTextFile`, `take`, `count`). Eso permite al optimizer eliminar operaciones redundantes antes de ejecutar.

**Por que el dataset pequeno puede no mostrar diferencia grande**: el overhead de arranque de Spark (conectarse al master, serializar el closure, distribuir el jar) es fijo y puede superar el tiempo de computo para pocos kilobytes. La ventaja de Spark crece con el volumen de datos.

## IMPORTANTE: expectativa de tiempos realista

Con el dataset incluido (4 archivos de texto, total ~3 KB), los tiempos tipicos son:
- MapReduce: 30-90 segundos (incluye arranque del ApplicationMaster, negociacion de containers YARN).
- Spark: 15-45 segundos (incluye arranque del driver y conexion al master).

La diferencia puede parecer pequena o incluso invertirse en la primera ejecucion. Esto es una oportunidad pedagogica, no un problema. Explicar que la diferencia se amplifica con:
- Datasets de varios GB.
- Algoritmos que iteran sobre los mismos datos (k-means, regresion, grafos).
- Pipelines con multiples etapas (cada etapa adicional en MR es otro ciclo completo de I/O en disco).

## Evidencias sugeridas

- Captura de `make ps` con los 10 servicios.
- Captura de Spark UI con los 2 workers registrados.
- Captura del job MapReduce completado en YARN UI.
- Captura del DAG del job Spark en Spark UI.
- Captura de la tabla de tiempos de `make compare`.
- Respuestas a las preguntas de analisis del Lab 4.

## Preguntas de cierre

1. Si tuvieras que procesar 10 TB de logs con una sola pasada de agregacion, ¿usarias MapReduce o Spark? ¿Por que?
2. Si tuvieras que entrenar un modelo de regresion logistica sobre 1 TB de datos con 100 iteraciones, ¿usarias MapReduce o Spark? ¿Por que?
3. ¿Que tendria que pasar para que MapReduce fuera la mejor opcion en un proyecto nuevo?
4. ¿Que limitacion tiene el wordcount en RDDs de Spark comparado con el equivalente en Spark SQL?
