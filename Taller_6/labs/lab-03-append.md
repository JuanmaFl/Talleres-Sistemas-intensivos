# Lab 3 — Ingestar un segundo lote y versionado con Iceberg

**Duracion estimada:** 25 minutos
**Prerequisito:** Lab 2 completado (pipeline ejecutado con el lote 1)
**Objetivo:** Entender como Iceberg gestiona multiples lotes de datos mediante snapshots.

---

## Contexto

En produccion, los datos de ventas no llegan todos de una vez.
Un nuevo archivo `ventas_lote2.csv` llega con los datos del Q2 2024 (abril-junio).
Necesitamos agregarlo a Bronze **sin sobreescribir** el lote anterior.

Iceberg hace esto a traves de `append()`, que genera un nuevo **snapshot** que apunta
a los datos nuevos mas los anteriores.

---

## Paso 1: Ver el estado actual de Bronze

En el notebook, ejecuta la celda de Bronze para confirmar el estado inicial:

```python
bronze = spark.sql("SELECT * FROM demo.lakehouse.bronze_ventas")
print(f"Total filas Bronze: {bronze.count()}")   # debe ser 30

spark.sql("""
    SELECT snapshot_id, committed_at, operation
    FROM demo.lakehouse.bronze_ventas.snapshots
""").show()   # debe haber 1 snapshot (el createOrReplace inicial)
```

---

## Paso 2: Ingestar el lote 2

En el notebook, ejecuta la celda **"Ingestar un segundo lote (append)"**:

```python
df_lote2 = spark.read.csv("/home/iceberg/data/ventas_lote2.csv", header=True, inferSchema=True)
df_lote2 = (
    df_lote2
    .withColumn("ingestion_ts", F.current_timestamp())
    .withColumn("source_file", F.lit("ventas_lote2.csv"))
)
df_lote2.writeTo("demo.lakehouse.bronze_ventas").append()

total_bronze = spark.sql("SELECT COUNT(*) FROM demo.lakehouse.bronze_ventas").collect()[0][0]
print(f"Total filas en Bronze ahora: {total_bronze}")   # debe ser 50
```

---

## Paso 3: Verificar los snapshots

Ejecuta la celda de historial de snapshots:

```python
spark.sql("""
    SELECT snapshot_id,
           committed_at,
           operation,
           summary['added-records']  AS registros_agregados,
           summary['total-records']  AS total_registros
    FROM demo.lakehouse.bronze_ventas.snapshots
    ORDER BY committed_at
""").show(truncate=False)
```

Deberian aparecer **2 snapshots**:
- El primero: operacion `overwrite` (del `createOrReplace`), `total-records` = 30.
- El segundo: operacion `append`, `added-records` = 20, `total-records` = 50.

---

## Paso 4: Re-ejecutar las transformaciones

Los datos de Silver y Gold aun solo tienen el lote 1. Actualiza las capas:

```bash
make transform
```

Luego en el notebook, vuelve a ejecutar las celdas de Silver y Gold para ver los nuevos totales.

Pregunta: ¿Cuanto subieron los ingresos totales en Gold al incluir el Q2?

---

## Paso 5 (opcional): Time travel — leer un snapshot anterior

Iceberg permite leer el estado de una tabla en un momento anterior.
Usando el `snapshot_id` del primer snapshot (el que tenia 30 filas):

```python
# Reemplaza <SNAPSHOT_ID_1> con el ID del primer snapshot
bronze_v1 = spark.sql("""
    SELECT COUNT(*) AS total
    FROM demo.lakehouse.bronze_ventas
    VERSION AS OF <SNAPSHOT_ID_1>
""")
bronze_v1.show()   # debe mostrar 30, no 50
```

Esto demuestra que los datos anteriores no se borraron — simplemente el snapshot
activo cambio.

---

## Preguntas de reflexion

1. Despues de ejecutar el lote 2, ¿cuantos snapshots tiene la tabla `bronze_ventas`?
   ¿Como lo verifica?

2. ¿Cual es la diferencia entre `writeTo(...).append()` y `writeTo(...).createOrReplace()`
   en terminos de:
   - Numero de snapshots generados
   - Datos perdidos/preservados
   - Caso de uso tipico

3. Silver y Gold usan `createOrReplace` en lugar de `append`. ¿Por que tiene sentido esa decision?
   Pista: piensa en idempotencia y en que pasa si re-ejecutas el pipeline dos veces.

4. Si quisieramos que Silver tambien mantuviera el historial (como Bronze), ¿que cambiariamos
   en `transform_silver.py`? ¿Habria algun riesgo con ese enfoque?

---

## Evidencia minima

- Captura del historial de snapshots mostrando los 2 snapshots con sus operaciones y `total-records`.
- Captura del output de `make transform` mostrando que Silver y Gold se actualizaron con los 50 registros.
- Captura de la celda de distribucion por `source_file` mostrando las dos fuentes.
