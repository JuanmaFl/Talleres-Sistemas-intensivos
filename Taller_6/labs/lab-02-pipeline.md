# Lab 2 — Ejecutar el pipeline Bronze → Silver → Gold

**Duracion estimada:** 30 minutos
**Prerequisito:** Lab 1 completado (entorno corriendo)
**Objetivo:** Ejecutar el pipeline completo de tres capas y explorar las tablas resultantes.

---

## Paso 1: Ingestar el lote 1 a Bronze

```bash
make ingest
```

Este comando ejecuta `jobs/ingest_bronze.py` dentro del contenedor de Spark.
Deberas ver una salida similar a:

```
=== Ingestando datos a Bronze ===
Bronze: 30 filas ingestadas exitosamente.
+---+----------+--------+...
Ingesion completada.
```

**¿Que hace este script?**
1. Lee `data/ventas_lote1.csv` (30 filas, Q1 2024).
2. Agrega las columnas `ingestion_ts` y `source_file`.
3. Escribe la tabla `demo.lakehouse.bronze_ventas` en MinIO usando `createOrReplace`.

---

## Paso 2: Transformar a Silver y Gold

```bash
make transform
```

Este comando ejecuta primero `transform_silver.py` y luego `transform_gold.py`.

Deberias ver:
```
=== Transformando a Silver ===
  Registros en Bronze: 30
  Registros validos: 30  (eliminados por limpieza: 0)
Silver: 30 filas escritas exitosamente.

=== Transformando a Gold ===
  Registros en Silver: 30
Gold: N filas de metricas generadas.
Transformacion completada.
```

---

## Paso 3: Explorar las tablas en el notebook

Abre el notebook `http://localhost:8888` → `mine/taller6.ipynb`.

Ejecuta las celdas en orden hasta la seccion "Capa Gold".

Presta atencion a:
- El schema de Bronze vs Silver: ¿que columnas nuevas aparecen?
- El schema de Gold: ¿cuantas filas tiene comparado con Silver? ¿Por que?

---

## Paso 4: Explorar los archivos en MinIO

Vuelve a **http://localhost:9001** y navega a:

```
warehouse → lakehouse → bronze_ventas
```

Deberias ver una estructura similar a:
```
warehouse/
  lakehouse/
    bronze_ventas/
      data/
        *.parquet       ← archivos de datos
      metadata/
        *.avro          ← manifests de Iceberg
        *.json          ← snapshot metadata
    silver_ventas/
      data/
      metadata/
    gold_metricas_region/
      data/
      metadata/
```

Haz clic en uno de los archivos `.parquet` — MinIO no puede abrirlo directamente
(es binario columnar), pero puedes ver su tamano y su nombre que incluye un UUID.

---

## Preguntas de reflexion

1. ¿Que columnas tiene Silver que NO tiene Bronze? Lista al menos 4.

2. ¿Que informacion pierde Gold en comparacion con Silver? Da un ejemplo concreto:
   ¿puedes saber desde Gold el `precio_unitario` de una venta especifica?

3. En MinIO, ¿cuantos archivos `.parquet` hay en `bronze_ventas/data/`?
   ¿Ese numero cambia si re-ejecutas `make ingest`? ¿Por que?

4. El script `transform_silver.py` hace un join LEFT entre las ventas y las dimensiones de productos.
   ¿Que pasaria si llega una venta de un producto que no existe en `dimensiones_productos.csv`?
   ¿Que valor tendria `proveedor` en ese caso? ¿Es un problema?

---

## Evidencia minima

- Captura del output de `make pipeline` (o `make ingest` + `make transform`) mostrando el count de cada capa.
- Captura del notebook con el schema de Silver (mostrando las columnas `proveedor`, `margen_pct`, `total`, `ganancia`).
- Captura de MinIO mostrando las tres carpetas de capas dentro del bucket `warehouse`.
