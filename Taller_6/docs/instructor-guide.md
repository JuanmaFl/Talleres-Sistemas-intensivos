# Guia del Instructor — Taller 6: Arquitectura Lakehouse

## Objetivo del taller

Integrar todos los conceptos del curso en un pipeline de datos real de punta a punta:
desde la ingestión de archivos CSV crudos hasta la consulta de metricas de negocio con Trino,
pasando por las tres capas de la arquitectura Medallion (Bronze, Silver, Gold).

Este taller no introduce muchas tecnologias nuevas — su valor pedagogico esta en **ver todo junto**:
MinIO (T5) + Spark + Iceberg (T5) + capas de calidad (nuevo) + Trino (nuevo).

## Requisitos previos

Los estudiantes deben haber completado el Taller 5 (MinIO + Spark + Iceberg).
Conceptos que se dan por conocidos: SparkSession, DataFrames, writeTo, snapshots de Iceberg, S3.

## Agenda (3 horas)

### Parte 1 — Contexto y arquitectura (40 min)

**20 min — Introduccion en pizarron: ¿que es un Lakehouse?**

Preguntas para arrancar la discusion:
- "En el Taller 5 escribimos una tabla Iceberg. Si al dia siguiente llega un nuevo archivo CSV,
  ¿que hacemos? ¿Sobreescribimos? ¿Concatenamos?"
- "Si un analista de negocio quiere consultar esos datos desde Excel o Tableau, ¿puede usar Spark?
  ¿Que necesitaria?"

Dibujar en el pizarron la progresion:
```
CSV → Spark → MinIO    (T5, todo junto)
                ↓
      Bronze / Silver / Gold   (T6, organizacion)
                ↓
      Trino → Analistas        (T6, multi-engine)
```

Enfatizar: **el catalogo REST es el pegamento**. Tanto Spark como Trino preguntan al mismo catalogo
donde estan las tablas. Por eso pueden trabajar con los mismos datos sin coordinacion manual.

**20 min — Levantar el entorno**

```bash
make up
```

Mientras los contenedores se inician (puede tomar 60-90 segundos), explicar el `docker-compose.yml`:
- Por que hay 5 servicios (minio, mc, rest, spark-iceberg, trino).
- Que hace `mc` automaticamente (crear los buckets `warehouse` y `raw`).
- Como Trino sabe donde estan los datos (via `config/trino/catalog/iceberg.properties`).

```bash
make status   # verificar que todos los servicios estan corriendo
```

### Parte 2 — Pipeline en accion (55 min)

**30 min — Ejecutar el pipeline completo**

```bash
make pipeline   # equivale a: make ingest && make transform
```

Mientras corre `ingest_bronze.py` (1-2 min), preguntar:
- "¿Que operacion Iceberg usa para escribir Bronze? (`createOrReplace`)"
- "¿Que columnas nuevas agrega que no estaban en el CSV?"

Mientras corre `transform_silver.py`:
- "¿Por que necesitamos el join con `dimensiones_productos.csv`?"
- "¿Que pasa si un producto del CSV no existe en el archivo de dimensiones?"

Mientras corre `transform_gold.py`:
- "¿Gold tiene una fila por venta? ¿O una fila por que?"
- "¿Que perdemos al pasar de Silver a Gold? ¿Cuando es aceptable esa perdida?"

**25 min — Explorar las capas en el notebook**

Abrir `http://localhost:8888` y ejecutar `notebooks/taller6.ipynb` celda a celda.

Detener en la celda de schemas:
- Comparar Bronze vs Silver: mostrar que Silver tiene `proveedor`, `margen_pct`, `total`, `ganancia`.
- Comparar Silver vs Gold: mostrar que Gold tiene solo metricas, no filas individuales.

Detener en la celda de historial de snapshots:
- Mostrar que Bronze tiene exactamente 1 snapshot (el `createOrReplace` inicial).
- Preguntar: "¿Cuantos snapshots tendra despues de agregar el lote 2?"

### Parte 3 — Lote 2 y Trino (45 min)

**20 min — Ingestar el segundo lote**

Ejecutar en el notebook la celda "Ingestar un segundo lote":
```python
df_lote2.writeTo("demo.lakehouse.bronze_ventas").append()
```

Mostrar:
- El count de Bronze sube de 30 a 50.
- El historial de snapshots ahora tiene 2 entradas.
- La celda de distribucion por `source_file` muestra los dos origenes.

Preguntar: "Si ahora re-ejecutamos `transform_silver.py` y `transform_gold.py`,
¿como va a cambiar Gold? ¿Que numeros esperamos ver?"

Re-ejecutar los scripts de transformacion y verificar.

**25 min — Consultas con Trino**

```bash
make query
```

Luego entrar al CLI interactivo:
```bash
docker compose exec trino trino --catalog iceberg --schema lakehouse
```

Ejecutar progresivamente:
```sql
SHOW TABLES;
SELECT * FROM gold_metricas_region LIMIT 5;
SELECT region, SUM(ingresos_totales) FROM gold_metricas_region GROUP BY region ORDER BY 2 DESC;
-- Consulta sobre Silver (datos no agregados)
SELECT producto, COUNT(*) AS ventas, SUM(total) AS ingresos FROM silver_ventas GROUP BY producto;
```

Abrir `http://localhost:8085` (Trino UI) para ver el query plan de la ultima consulta.
Preguntar: "¿Trino inicio una SparkSession? ¿Como lee los archivos Parquet?"

### Parte 4 — Discusion final del curso (40 min)

**Preguntas de cierre del curso completo:**

1. **Progresion tecnologica**: "¿Que era mas complejo de escribir en el Taller 2 con MapReduce
   versus este taller con Spark? ¿Que ganamos con la abstraccion?"

2. **Storage evolution**: "En T2 usabamos HDFS. En T6 usamos MinIO. ¿Que ventajas tiene
   separar el storage del compute?"

3. **Formato de datos**: "En T2 eran archivos de texto plano. En T6 son archivos Parquet
   con metadatos Iceberg. ¿Que nos da eso que el texto plano no puede dar?"

4. **Multi-engine**: "¿Por que queremos que Trino Y Spark puedan leer las mismas tablas?
   ¿No es mas simple tener solo una herramienta?"

5. **Produccion**: "Si este sistema fuera de produccion real, ¿que le faltaria?
   (Respuestas esperadas: scheduling/Airflow, monitoreo, CI/CD, autenticacion, compaction de Iceberg)"

6. **Cloud**: "¿Que cambiaria si reemplazamos MinIO por AWS S3 y Trino por Amazon Athena?"

## Conceptos a enfatizar a lo largo del taller

- **Separacion de responsabilidades entre capas**: cada capa tiene un contrato claro con sus consumidores.
  No se hacen transformaciones de negocio en Bronze. No se agregan datos en Silver.

- **Catalogo compartido como componente critico**: sin el REST catalog, Spark y Trino no podrian
  ver las mismas tablas. Es equivalente al Hive Metastore en ecosistemas Hadoop, pero con protocolo REST.

- **Compute vs Storage**: MinIO no sabe de Spark ni de Trino. Spark y Trino no saben como replica
  MinIO los datos. La separacion permite escalar cada capa independientemente.

- **Idempotencia**: `createOrReplace` en Silver y Gold garantiza que re-ejecutar el pipeline
  produce el mismo resultado. `append` en Bronze garantiza que no se pierden lotes previos.

- **Trino no necesita Spark**: Trino lee directamente los archivos Parquet en MinIO usando
  el catalogo para saber donde estan. Esto es fundamentalmente diferente a "ejecutar Spark a traves de Trino".

## Errores comunes de los estudiantes

| Error | Como manejarlo |
|-------|---------------|
| `make pipeline` falla porque los servicios no estan listos | `make status` para verificar, esperar 30s mas y reintentar |
| Trino no ve las tablas | Verificar que `make pipeline` corrio completo; el catalogo se llena cuando Spark escribe |
| El count de Silver es menor que Bronze | Es correcto si habia datos invalidos; explicar que eso es el punto de la limpieza |
| La celda de append falla con "tabla no existe" | `make ingest` debe correr primero |
| Trino UI muestra 0 queries | Normal al arrancar; ejecutar `make query` primero |

## Material de apoyo incluido en el repositorio

- `docs/brief.md`: contexto del problema que resuelve el Lakehouse.
- `docs/architecture.md`: diagrama Mermaid y comparacion con arquitectura HDFS.
- `labs/lab-01-entorno.md` a `lab-04-trino.md`: guias paso a paso para los estudiantes.
- `notebooks/taller6.ipynb`: notebook con preguntas integradas al final de cada seccion.
