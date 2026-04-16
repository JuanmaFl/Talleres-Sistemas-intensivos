# Resumen del Taller 3 — De MapReduce a Spark

## Contexto

Este taller es la continuacion directa del Taller 2. En ese taller, los estudiantes levantaron un cluster Hadoop, cargaron archivos en HDFS y ejecutaron un wordcount usando el `hadoop-mapreduce-examples.jar`. Ya conocen el ciclo map-shuffle-reduce y saben leer la salida de un job en YARN UI.

El punto de partida de esta sesion es la pregunta que surge naturalmente al terminar el Taller 2: **si MapReduce funciona, ¿por que el mundo adopto Spark?**

## Problema pedagogico

Los estudiantes han escuchado que Spark es "mucho mas rapido" que MapReduce. Sin embargo, esa afirmacion abstracta no ancla a nada concreto si no se comparan los dos engines resolviendo el **mismo problema, sobre los mismos datos, en el mismo entorno**.

El riesgo pedagogico es que los estudiantes asuman que Spark siempre es mejor sin entender por que: Spark mantiene datos en memoria, usa un DAG en lugar de etapas discretas, y pospone la ejecucion hasta que el resultado es necesario. Sin esa comprension, no podran elegir el engine correcto en un proyecto real.

## Solucion

El taller propone ejecutar wordcount dos veces sobre exactamente los mismos archivos de texto:

1. Con MapReduce (usando el mismo jar del Taller 2), midiendo el tiempo.
2. Con Spark (usando el script PySpark en `jobs/wordcount.py`), midiendo el tiempo.

El comando `make compare` ejecuta ambos en secuencia y muestra una tabla comparativa de tiempos. El estudiante puede ver el numero, analizar el DAG en Spark UI y contrastar con el plan de ejecucion en YARN UI.

Ademas del tiempo, el taller compara el codigo: el WordCount en Java con MapReduce requiere aproximadamente 60 lineas con clases Mapper, Reducer y Driver; el equivalente en PySpark tiene menos de 15 lineas.

## Dataset

Se usan los mismos 3 archivos de texto del Taller 2 (`introduccion.txt`, `hdfs.txt`, `mapreduce.txt`) mas un cuarto archivo nuevo (`spark.txt`) con contenido educativo sobre Spark. Esto permite que la comparacion sea directa y que los estudiantes que completan el Taller 2 reconozcan los datos.

El dataset es intencionalmente pequeno. Con pocos kilobytes de texto la diferencia de tiempo puede ser modesta porque el overhead de inicializar la JVM de Spark es comparable al tiempo de ejecucion. Eso es parte de la leccion: la ventaja de Spark se amplifica con datasets mas grandes y con operaciones iterativas.

## Objetivo de exito

Al terminar el taller, el estudiante debe ser capaz de:

- Explicar por que Spark es mas eficiente que MapReduce para datos que caben en memoria (in-memory shuffle, DAG, lazy evaluation).
- Describir que son los RDDs y como se relacionan con los pares clave-valor de MapReduce.
- Leer el DAG de una aplicacion Spark en la Spark UI e identificar stages y tasks.
- Reconocer cuando MapReduce podria seguir siendo preferible (tolerancia a fallos extrema, datasets que no caben en memoria del cluster, integracion con sistemas legacy).
- Anticipar lo que viene en el Taller 4: DataFrames y Parquet como siguiente nivel de abstraccion sobre Spark.
