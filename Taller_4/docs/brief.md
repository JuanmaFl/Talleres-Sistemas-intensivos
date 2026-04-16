# Brief — Taller 4: Spark con Datos Estructurados

## Problema

Al finalizar el Taller 3, los estudiantes saben lanzar un job de Spark y comparar
su velocidad frente a MapReduce. Sin embargo, el ejercicio (wordcount) opera sobre
texto plano y usa la API de bajo nivel (RDDs), que replica el modelo key-value de
Hadoop.

En la industria, la gran mayoria de los flujos de datos trabajan con **tablas
estructuradas**: registros de ventas, logs de eventos, datos de sensores. Para esos
casos, Spark ofrece la **DataFrame API** y **Spark SQL**, abstracciones de alto nivel
que ocultan el shuffle y permiten optimizaciones automaticas (Catalyst Optimizer).
Ademas, los datos estructurados rara vez viven en CSV: el formato columnar **Parquet**
es el estandar de facto en lagos de datos modernos.

## Solucion propuesta

| Componente | Descripcion |
|---|---|
| Dataset | 50 registros de ventas ficticias en CSV (columnas de negocio reales) |
| Ingesta | `spark.read.csv` con `inferSchema=True` |
| Transformacion | DataFrame API: `withColumn`, `groupBy`, `agg`, `orderBy` |
| Persistencia | Escritura en formato Parquet con `df.write.parquet(...)` |
| Consulta | Spark SQL sobre una TempView del DataFrame Parquet |

## Dataset

Archivo: `data/ventas.csv`
Filas: 50 (mas header)
Columnas: `id`, `fecha`, `producto`, `categoria`, `cantidad`, `precio_unitario`, `region`
Periodo cubierto: enero 2024 — junio 2024
Productos: Laptop, Teclado, Monitor, Mouse, Auriculares, Webcam, Disco SSD, RAM, Tablet, Smartphone
Categorias: Electronica, Perifericos, Almacenamiento, Movil
Regiones: Bogota, Medellin, Cali, Barranquilla, Bucaramanga

Los valores de precio estan en pesos colombianos (COP).

## Usuarios

Estudiantes universitarios de un curso de Sistemas Intensivos en Datos.
Se asume conocimiento previo de Docker, HDFS y la API basica de Spark RDDs.

## Objetivos de exito

Un estudiante completa el taller cuando puede demostrar que:

1. Lee un CSV desde Spark y verifica el schema inferido.
2. Aplica transformaciones con la DataFrame API (nueva columna, filtro, agrupacion).
3. Escribe el resultado en formato Parquet.
4. Vuelve a leer el Parquet y ejecuta al menos una consulta con Spark SQL.
5. Explica con sus propias palabras por que Parquet es mas eficiente que CSV para
   consultas analiticas.
