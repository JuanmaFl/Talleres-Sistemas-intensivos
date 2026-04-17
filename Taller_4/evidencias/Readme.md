# Taller 4 — Spark con Datos Estructurados

**Equipo:** Samuel Molina · David Felipe Ríos · Juan Manuel Flórez  
**Curso:** Sistemas Intensivos en Datos — Universidad EAFIT  
**Fecha:** Abril 2026  

---

## Qué se hizo

El objetivo era dejar de usar la API de RDDs de Spark (que es básicamente MapReduce con mejor sintaxis) y trabajar con DataFrames, Parquet y Spark SQL sobre un dataset de ventas reales simuladas. 50 registros, 7 columnas, productos de electrónica vendidos en cinco ciudades colombianas entre enero y junio de 2024.

El taller se divide en cuatro labs que van escalando: primero leer el CSV y ver el schema, luego transformar con la DataFrame API, luego persistir en Parquet, luego consultar con SQL.

---

## Infraestructura

El cluster corre completamente local con Docker. Cuatro contenedores:

- `spark-master` — imagen `apache/spark:latest`
- `spark-worker-1` y `spark-worker-2` — misma imagen, 1G RAM / 2 cores cada uno
- `jupyter` — imagen `jupyter/pyspark-notebook:latest`

**Problema con las imágenes de Spark:** `bitnami/spark:3.5` y `bitnami/spark:3.4.1` no estaban disponibles en Docker Hub. Se intentó con `apache/spark:latest` pero los workers se cerraban porque la imagen no reconoce variables de entorno como `SPARK_MODE`. La solución fue correr los jobs con `spark-submit --master local[*]` directo sobre el contenedor del master, sin necesidad de que los workers estuvieran activos como cluster standalone.

**Problema con PySpark en Jupyter:** La versión de PySpark instalada en Jupyter no coincidía con Spark 4.1.1 que trae la imagen de Apache, generando `TypeError: 'JavaPackage' object is not callable`. Se resolvió ejecutando todos los scripts con `spark-submit` desde PowerShell en lugar de notebooks.

---

## Evidencias

### Lab 1 — Cluster Setup y lectura de CSV

**Archivo:** `Lab1.png`

Muestra la ejecución de `test_local.py`. Spark levantó en modo local, leyó `ventas.csv` y mostró las primeras 5 filas con su schema inferido correctamente:

- `id`: integer
- `fecha`: date
- `producto`, `categoria`, `region`: string
- `cantidad`, `precio_unitario`: integer

Spark infirió todos los tipos sin configuración adicional. El SparkContext se cerró limpiamente con uptime de 5733 ms.

---

### Lab 2 — DataFrame API

**Archivos:** `Lab2_1.png`, `Lab2_2.png`, `Lab2_3.png`, `Lab2_4.png`

**Lab2_1.png** — DataFrame original con 3 filas y el schema. Muestra que el CSV tiene 7 columnas y que `inferSchema=True` funcionó igual que en el Lab 1.

**Lab2_2.png** — Resultado de `withColumn("total", cantidad * precio_unitario)` sobre las primeras 5 filas. La Laptop tiene total de 5.600.000, el Mouse de 225.000. Además se ve el inicio de la agregación por región con logs del DAG scheduler.

**Lab2_3.png** — Tabla de ventas por región y tabla de ventas por categoría:

| region | num_ventas | total_ingresos |
|---|---|---|
| Bogotá | 17 | 31.265.000 |
| Medellín | 12 | 18.285.000 |
| Cali | 9 | 17.850.000 |
| Barranquilla | 7 | 8.240.000 |
| Bucaramanga | 5 | 7.450.000 |

Categorías por cantidad vendida: Periféricos lidera en unidades (83), Electrónica en precio promedio (1.890.000 COP).

**Lab2_4.png** — Columna `venta_alta` calculada con `when()`. Cualquier transacción con total >= 3.000.000 queda marcada como "Si". Solo Laptop (id 1) y Smartphone (id 10) califican en las primeras 10 filas. El script cerró correctamente al final.

---

### Lab 3 — Parquet

**Archivos:** `Lab3_1.png`, `Lab3_2.png`, `Lab3_3.png`

**Lab3_1.png** — Column Pruning: se leyó el Parquet seleccionando solo `region` y `total`. El log confirma que Spark usó `InMemoryFileIndex` y el archivo quedó en `/tmp/ventas_processed.parquet`. Luego se ve el inicio del Predicate Pushdown con filtro `total > 2.000.000`.

**Lab3_2.png** — Resultado del Predicate Pushdown. 15 registros superan los 2 millones. Se destacan Laptop en Bogotá (5.600.000), Tablet en Medellín (3.600.000) y Monitor en Medellín (2.940.000). Los filtros se aplican antes de leer el archivo completo.

**Lab3_3.png** — Agregación final sobre Parquet por categoría:

| categoria | ingresos_totales | ingresos_promedio |
|---|---|---|
| Electronica | 33.040.000 | 3.304.000 |
| Movil | 28.200.000 | 2.820.000 |
| Almacenamiento | 12.220.000 | 1.222.000 |
| Perifericos | 9.630.000 | 481.500 |

Electrónica domina en ingresos totales aunque Periféricos vende más unidades (lo vimos en Lab 2). Eso tiene sentido: Mouse y Teclado son baratos pero se venden bastante.

---

### Lab 4 — Spark SQL

**Archivos:** `Lab4_1.png`, `Lab4_2.png`, `Lab4_3.png`, `Lab4_4.png`

**Lab4_1.png** — Top 5 ventas por monto usando SQL. La Laptop de Cali (id 21) encabeza con 8.400.000, seguida por dos Laptops de Bogotá (ids 1 y 41) con 5.600.000 cada una. La TempView `ventas` se creó correctamente sobre el Parquet del Lab 3.

**Lab4_2.png** — `GROUP BY region` con SQL. Los números coinciden exactamente con Lab 2 (buen signo: el Parquet es fiel al CSV). Se ve que el FileSourceStrategy aplicó Pushed Filters automáticamente.

**Lab4_3.png** — `HAVING SUM(total) > 5.000.000` filtrando categorías. Las cuatro categorías superan ese umbral. Electrónica: 33 millones, Móvil: 28 millones, Almacenamiento: 12 millones, Periféricos: 9,6 millones.

**Lab4_4.png** — Top 3 productos por región con `ROW_NUMBER() OVER (PARTITION BY region)`. En Barranquilla gana Smartphone, Laptop y RAM. En Bogotá dos Laptops y una Tablet. El script también intentó guardar el resumen en `/data/resumen_ventas.csv` pero `/data` es read-only en el contenedor (bind mount con `:ro`). Ese último paso falló con error de permisos, lo cual no afecta los resultados de SQL.

---

## Scripts entregados

| Archivo | Propósito |
|---|---|
| `jobs/test_local.py` | Lab 1: schema inference y lectura básica |
| `jobs/lab2_dataframe_api.py` | Lab 2: withColumn, groupBy, agg, when |
| `jobs/lab3_parquet.py` | Lab 3: escribir/leer Parquet, column pruning, predicate pushdown |
| `jobs/lab4_sql.py` | Lab 4: TempView, GROUP BY, HAVING, Window functions |
| `jobs/analisis_completo.py` | Reporte consolidado: resumen general, por región, por categoría, top 10 |

---

## Cómo reproducir

```powershell
cd "ruta/al/taller_4"

# Levantar cluster
docker compose up -d

# Lab 1
docker compose exec spark-master /opt/spark/bin/spark-submit --master local[*] /jobs/test_local.py

# Lab 2
docker compose exec spark-master /opt/spark/bin/spark-submit --master local[*] /jobs/lab2_dataframe_api.py

# Lab 3
docker compose exec spark-master /opt/spark/bin/spark-submit --master local[*] /jobs/lab3_parquet.py

# Lab 4 (requiere que Lab 3 haya corrido primero)
docker compose exec spark-master /opt/spark/bin/spark-submit --master local[*] /jobs/lab4_sql.py

# Reporte final
docker compose exec spark-master /opt/spark/bin/spark-submit --master local[*] /jobs/analisis_completo.py
```

**Nota:** El Lab 4 lee el Parquet que genera el Lab 3. Hay que correrlos en orden.

---

## Problemas encontrados

**1. Imágenes de Bitnami no disponibles**  
`bitnami/spark:3.5` y `bitnami/spark:3.4.1` dan 404 en Docker Hub. Se migró a `apache/spark:latest`.

**2. Workers de Spark se cerraban solos**  
`apache/spark:latest` no reconoce `SPARK_MODE=worker`. Sin un script de arranque explícito, el contenedor se cierra con exit code 127. Se dejaron los workers corriendo con `sleep infinity` y se usó `local[*]` para los jobs.

**3. PySpark en Jupyter incompatible con Spark 4.1.1**  
El notebook de Jupyter lanzaba `TypeError: 'JavaPackage' object is not callable` porque la versión de PySpark instalada era 3.x y la imagen de Spark ya es 4.1.1. Solución: todos los scripts se ejecutan con `spark-submit` desde PowerShell.

**4. `/data` es read-only**  
El bind mount de Docker se montó con `:ro`, entonces cualquier escritura a `/data/` falla. Los Parquet intermedios se guardan en `/tmp/` dentro del contenedor. El CSV de resumen del Lab 4 no se pudo guardar, pero los resultados SQL sí se mostraron correctamente.

**5. `make` no existe en Windows**  
El Makefile del proyecto no funciona en CMD ni PowerShell. Todos los comandos se tradujeron a `docker compose exec` manualmente.