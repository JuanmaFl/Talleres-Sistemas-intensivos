# Taller 6 — Lakehouse: Pipeline Bronze-Silver-Gold con Spark, Iceberg y Trino

Taller final de la serie. Construye un pipeline de datos completo sobre una arquitectura
Lakehouse usando MinIO como object storage, Apache Iceberg como open table format,
Spark para el procesamiento ETL y Trino como motor SQL independiente para analistas.

---

## Objetivos de aprendizaje

Al completar este taller el estudiante podra:

1. Explicar la arquitectura Medallion (Bronze / Silver / Gold) y el proposito de cada capa.
2. Ejecutar un pipeline ETL completo con Spark que produzca las tres capas.
3. Ingestar lotes sucesivos de datos usando `append` en tablas Iceberg y observar el versionado.
4. Consultar tablas Iceberg con Trino de forma independiente a Spark, entendiendo el rol del catalogo REST.
5. Relacionar este taller con la progresion tecnologica del curso (de MapReduce a Lakehouse).

---

## Arquitectura

```
  [CSV raw files]
       |
       v
  Spark (ingest_bronze.py)
  +-- agrega ingestion_ts, source_file
       |
       v
  Bronze (Iceberg / MinIO)
  s3://warehouse/lakehouse/bronze_ventas/
       |
       v
  Spark (transform_silver.py)
  +-- limpieza, join con dimensiones, total, ganancia
       |
       v
  Silver (Iceberg / MinIO)
  s3://warehouse/lakehouse/silver_ventas/
       |
       v
  Spark (transform_gold.py)
  +-- agrupacion por region, categoria y mes
       |
       v
  Gold (Iceberg / MinIO)
  s3://warehouse/lakehouse/gold_metricas_region/
       |
       +---> Trino CLI / Trino UI   <-- analistas SQL (sin Spark)
       +---> Spark SQL / Notebook   <-- ingenieros de datos

  REST Catalog (iceberg-rest:8181) <-- compartido entre Spark y Trino
```

---

## Estructura del repositorio

```
Taller_6/
|-- docker-compose.yml          # 5 servicios: minio, mc, rest, spark-iceberg, trino
|-- Makefile                    # comandos: up, down, pipeline, query, status, ...
|-- README.md
|
|-- config/
|   |-- trino/
|       |-- catalog/
|       |   |-- iceberg.properties   # conector Iceberg para Trino
|       |-- config.properties
|       |-- node.properties
|       |-- jvm.config
|
|-- data/
|   |-- ventas_lote1.csv             # 30 filas Q1 2024
|   |-- ventas_lote2.csv             # 20 filas Q2 2024 (segundo lote)
|   |-- dimensiones_productos.csv    # proveedor y margen por producto
|
|-- jobs/
|   |-- ingest_bronze.py             # CSV -> tabla Bronze Iceberg
|   |-- transform_silver.py          # Bronze -> Silver (limpieza + enriquecimiento)
|   |-- transform_gold.py            # Silver -> Gold (metricas agregadas)
|
|-- scripts/
|   |-- ingest.sh                    # make ingest
|   |-- transform.sh                 # make transform
|   |-- query.sh                     # make query (Trino CLI)
|   |-- status.sh                    # make status
|
|-- notebooks/
|   |-- taller6.ipynb                # notebook Jupyter interactivo
|
|-- docs/
|   |-- brief.md                     # problema que resuelve el Lakehouse
|   |-- architecture.md              # diagrama Mermaid + comparacion HDFS
|   |-- instructor-guide.md          # agenda, conceptos, errores comunes
|
|-- labs/
    |-- lab-01-entorno.md            # levantar y verificar el entorno
    |-- lab-02-pipeline.md           # ejecutar el pipeline Bronze-Silver-Gold
    |-- lab-03-append.md             # segundo lote y snapshots Iceberg
    |-- lab-04-trino.md              # consultas SQL con Trino
```

---

## Requisitos

- **Docker Desktop** 4.x o superior con Docker Compose V2
- **RAM disponible**: minimo 8 GB (recomendado 10 GB)
  - MinIO: ~256 MB
  - Iceberg REST: ~256 MB
  - Spark: ~3-4 GB (JVM + executor)
  - Trino: ~2 GB (JVM configurado con `-Xmx2G`)
- Puertos libres: 8080, 8085, 8181, 8888, 9000, 9001

---

## Inicio rapido

```bash
# 1. Levantar todos los servicios
make up

# 2. Esperar ~90 segundos y verificar
make status

# 3. Ejecutar el pipeline completo (ingest + transform)
make pipeline

# 4. Consultar Gold con Trino
make query

# 5. Explorar en el notebook
# Abrir http://localhost:8888 -> mine/taller6.ipynb
```

---

## Interfaces de usuario

| Interfaz         | URL                        | Credenciales         |
|------------------|----------------------------|----------------------|
| Jupyter + Spark  | http://localhost:8888      | Sin autenticacion    |
| Spark UI         | http://localhost:8080      | Sin autenticacion    |
| MinIO Console    | http://localhost:9001      | admin / password123  |
| Iceberg REST     | http://localhost:8181      | Sin autenticacion    |
| Trino UI         | http://localhost:8085      | Sin autenticacion    |

---

## Flujo del taller

### Lab 1 — Entorno (20 min)
Levantar los servicios, explorar MinIO y Trino UI, abrir el notebook.

### Lab 2 — Pipeline (30 min)
```bash
make pipeline
```
Explorar Bronze, Silver y Gold en el notebook. Ver los archivos en MinIO.

### Lab 3 — Segundo lote (25 min)
En el notebook, ejecutar la celda de append del lote 2.
Ver el versionado de snapshots en Iceberg. Re-ejecutar las transformaciones.

### Lab 4 — Trino (25 min)
```bash
make query                                          # query preconfigurado
docker compose exec trino trino --catalog iceberg --schema lakehouse  # CLI interactivo
```
Explorar la Trino UI, ejecutar queries analiticos, comparar con Spark SQL.

---

## Comandos utiles

```bash
make up           # iniciar el entorno
make down         # detener el entorno (preserva datos)
make clean        # detener y eliminar volumenes (borra todos los datos)
make ps           # estado de los contenedores
make logs         # logs de spark-iceberg y trino
make ingest       # ingestar lote 1 a Bronze
make transform    # transformar Silver + Gold
make pipeline     # ingest + transform
make query        # consultar Gold con Trino CLI
make status       # estado + URLs de las interfaces

# Acceder a Spark directamente
docker compose exec spark-iceberg spark-sql

# Acceder a Trino CLI
docker compose exec trino trino --catalog iceberg --schema lakehouse

# Ejecutar un job manualmente
docker compose exec spark-iceberg spark-submit /home/iceberg/jobs/ingest_bronze.py
```

---

## Material docente incluido

| Archivo                       | Descripcion                                      |
|-------------------------------|--------------------------------------------------|
| `docs/brief.md`               | Problema de negocio que motiva el Lakehouse      |
| `docs/architecture.md`        | Diagrama Mermaid, comparacion HDFS vs Lakehouse  |
| `docs/instructor-guide.md`    | Agenda de 3 horas, conceptos clave, errores      |
| `labs/lab-01-entorno.md`      | Guia paso a paso: verificar el entorno           |
| `labs/lab-02-pipeline.md`     | Guia paso a paso: ejecutar el pipeline           |
| `labs/lab-03-append.md`       | Guia paso a paso: segundo lote y snapshots       |
| `labs/lab-04-trino.md`        | Guia paso a paso: queries con Trino              |

---

## Cierre del ciclo: progresion de los talleres

| Taller | Nombre                        | Storage      | Engine         | Formato   | Concepto clave                          |
|--------|-------------------------------|--------------|----------------|-----------|-----------------------------------------|
| T2     | HDFS + MapReduce              | HDFS         | MapReduce      | Text/CSV  | Procesamiento distribuido basico        |
| T3     | HDFS + Spark                  | HDFS         | Spark          | Text/CSV  | Spark como reemplazo de MapReduce       |
| T4     | Spark + DataFrames + Parquet  | HDFS / local | Spark          | Parquet   | Formatos columnar y DataFrames          |
| T5     | MinIO + Spark + Iceberg       | MinIO (S3)   | Spark          | Iceberg   | Open table formats y snapshots          |
| **T6** | **Lakehouse completo**        | MinIO (S3)   | Spark + Trino  | Iceberg   | Capas de calidad y catalogo compartido  |

La progresion refleja la evolucion real de la industria de datos en la ultima decada:
del cluster Hadoop monolitico al Lakehouse moderno con separacion de compute y storage.
