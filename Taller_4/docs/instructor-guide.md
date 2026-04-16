# Guia del Instructor — Taller 4: Spark con Datos Estructurados

## Objetivo del taller

Demostrar que Spark **no es solo "MapReduce rapido"** sino una plataforma con una
API de alto nivel orientada al analisis de datos estructurados. Al finalizar, los
estudiantes deben entender:

- La diferencia entre RDDs (Taller 3) y DataFrames (Taller 4).
- Como Spark infiere y valida esquemas de datos.
- Por que Parquet domina en los lagos de datos modernos.
- Que Spark SQL permite usar el conocimiento de SQL directamente sobre DataFrames.

---

## Agenda sugerida (2.5 horas)

| Tiempo | Actividad |
|---|---|
| 00:00 — 00:15 | Repaso Taller 3 + introduccion a DataFrames |
| 00:15 — 00:35 | Levantar cluster + abrir Jupyter (Lab 1) |
| 00:35 — 01:05 | DataFrame API interactiva (Lab 2) |
| 01:05 — 01:30 | Parquet: escribir, leer, comparar tamano (Lab 3) |
| 01:30 — 01:50 | Spark SQL (Lab 4) |
| 01:50 — 02:10 | Discusion, preguntas y cierre |
| 02:10 — 02:30 | Buffer / retos opcionales |

---

## Conceptos clave a enfatizar

### 1. Schema inference

`inferSchema=True` hace que Spark lea una muestra del archivo para deducir los
tipos de cada columna. Sin el, todos los campos llegan como `StringType`, lo que
obliga a castear manualmente. Mostrar el contraste con `df.printSchema()`.

### 2. Lazy evaluation

Las transformaciones (`withColumn`, `filter`, `groupBy`) **no ejecutan nada** hasta
que se llama una accion (`show`, `count`, `write`). Esto permite a Catalyst
Optimizer reordenar y combinar operaciones.

**Tip:** ejecutar `df.explain()` o `df.explain("extended")` justo antes de un
`show()` para mostrar el plan fisico. Los estudiantes suelen sorprenderse al ver
que Spark reordena sus filtros.

```python
df.filter(F.col("region") == "Bogota") \
  .groupBy("producto") \
  .agg(F.sum("total")) \
  .explain()
```

### 3. Almacenamiento columnar (Parquet)

En un formato por filas (CSV, JSON), leer una sola columna requiere recorrer todo
el archivo. En Parquet, cada columna se almacena contigua en disco; leer 2 columnas
de 100 solo toca 2% de los datos.

Mostrar la diferencia con `!du -sh /home/jovyan/data/ventas.csv` y el directorio
Parquet en `/tmp/ventas_parquet`. Con solo 50 filas la diferencia es pequena, pero
el patron escala.

### 4. Predicate pushdown

Cuando Spark lee Parquet y encuentra un `filter`, puede descartar bloques de datos
antes de cargarlos en memoria. Esto se ve en el plan de ejecucion como
`PushedFilters`.

### 5. TempView y duracion de sesion

`createOrReplaceTempView("ventas")` registra el DataFrame como tabla **solo para
esa SparkSession**. Si el kernel de Jupyter se reinicia, la vista desaparece. Esto
contrasta con las tablas permanentes de un Hive Metastore (tema del Taller 5).

---

## Errores frecuentes de los estudiantes

| Error | Causa | Solucion |
|---|---|---|
| `AnalysisException: Path does not exist` | El archivo CSV no esta montado | Verificar que `./data` existe en el host y que el compose esta corriendo |
| `Connection refused` al crear SparkSession | El master no esta listo | Esperar 10-15 s despues de `make up` y reintentar |
| Columnas con tipo `string` en lugar de `int` | Olvidaron `inferSchema=True` | Agregar el parametro o usar un schema explicito |
| `show()` no muestra todos los decimales | Comportamiento por defecto de Spark | Usar `df.show(truncate=False)` |

---

## Evidencias sugeridas para evaluacion

- Captura del schema inferido (`df.printSchema()`).
- Tabla con ventas agrupadas por region (Lab 2).
- Confirmacion de escritura Parquet (mensaje de consola o `ls /tmp/ventas_parquet`).
- Resultado de al menos una consulta SQL (Lab 4).
- Respuesta escrita a: "¿por que Parquet es mas eficiente para consultas analiticas?"

---

## Conexion con la serie de talleres

| Taller | Tecnologia | Pregunta central |
|---|---|---|
| 2 | HDFS + MapReduce | ¿Como distribuir almacenamiento y computo? |
| 3 | HDFS + Spark RDD | ¿Puede Spark reemplazar MapReduce? |
| **4** | **Spark DataFrame + Parquet** | **¿Como trabajar con datos estructurados a escala?** |
| 5 | MinIO + Iceberg | ¿Como gestionar tablas en un data lake real? |
