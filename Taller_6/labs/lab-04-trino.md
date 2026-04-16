# Lab 4 — Consultas analiticas con Trino

**Duracion estimada:** 25 minutos
**Prerequisito:** Labs 1-3 completados (pipeline ejecutado, datos en las tres capas)
**Objetivo:** Entender que Trino puede consultar las tablas Iceberg de forma independiente de Spark,
y explorar sus capacidades como motor SQL analitico.

---

## Contexto

Hasta ahora hemos usado **Spark** para leer y escribir las tablas Iceberg.
Spark es potente para transformaciones complejas, pero requiere JVM, una SparkSession
y generalmente esta pensado para ingenieros de datos.

**Trino** es un motor SQL distribuido que puede leer directamente las tablas Iceberg
usando el catalogo REST. No necesita iniciar una SparkSession. Un analista puede conectarse
con cualquier cliente SQL estandar (JDBC, ODBC, CLI) y ejecutar queries.

---

## Paso 1: Consulta rapida con make query

```bash
make query
```

Deberia mostrar las metricas de la tabla Gold ordenadas por ingresos:

```
 region      | ingresos_totales | num_transacciones
-------------+------------------+------------------
 Bogota      |         XXXXX.XX |               XX
 Medellin    |         XXXXX.XX |               XX
 ...
```

Este comando no inicio Spark. Trino leyo directamente los archivos Parquet en MinIO.

---

## Paso 2: Entrar al CLI interactivo de Trino

```bash
docker compose exec trino trino --catalog iceberg --schema lakehouse
```

Deberias ver el prompt:
```
trino:lakehouse>
```

---

## Paso 3: Explorar el catalogo desde Trino

```sql
-- Ver tablas disponibles
SHOW TABLES;

-- Ver esquema de una tabla
DESCRIBE gold_metricas_region;

-- Ver esquema de Silver
DESCRIBE silver_ventas;
```

Observa que Trino conoce el schema exacto de las tablas — lo obtuvo del REST catalog,
que a su vez lo obtuvo cuando Spark escribio las tablas.

---

## Paso 4: Queries analiticas sobre Gold

```sql
-- Ingresos totales por region
SELECT region,
       SUM(ingresos_totales)  AS ingresos_totales,
       SUM(ganancia_total)    AS ganancia_total,
       SUM(num_transacciones) AS num_transacciones
FROM gold_metricas_region
GROUP BY region
ORDER BY ingresos_totales DESC;

-- Ingresos por categoria
SELECT categoria,
       SUM(ingresos_totales) AS ingresos_totales
FROM gold_metricas_region
GROUP BY categoria
ORDER BY ingresos_totales DESC;

-- Evolucion mensual de ingresos (todos los meses)
SELECT anio_mes,
       SUM(ingresos_totales) AS ingresos_mes
FROM gold_metricas_region
GROUP BY anio_mes
ORDER BY anio_mes;
```

---

## Paso 5: Queries sobre Silver (granularidad de transaccion)

```sql
-- Top 5 productos por ingreso
SELECT producto,
       COUNT(*)       AS num_ventas,
       SUM(total)     AS ingresos,
       SUM(ganancia)  AS ganancia
FROM silver_ventas
GROUP BY producto
ORDER BY ingresos DESC
LIMIT 5;

-- Comparar Q1 vs Q2
SELECT CASE
         WHEN CAST(fecha AS DATE) BETWEEN DATE '2024-01-01' AND DATE '2024-03-31' THEN 'Q1'
         WHEN CAST(fecha AS DATE) BETWEEN DATE '2024-04-01' AND DATE '2024-06-30' THEN 'Q2'
       END AS trimestre,
       SUM(total) AS ingresos_totales
FROM silver_ventas
GROUP BY 1
ORDER BY 1;
```

---

## Paso 6: Explorar Trino UI

Abre **http://localhost:8085** en el navegador.

1. Ejecuta uno de los queries del Paso 4 en el CLI.
2. Vuelve al navegador y ve a la pestana **Query Detail**.
3. Haz clic en el query mas reciente.
4. Explora:
   - **Overview**: tiempo de ejecucion, bytes leidos, numero de splits.
   - **Live Plan**: el plan de ejecucion del query (stages y operadores).
   - **Splits**: distribucion del trabajo entre los workers.

Pregunta: ¿Cuantos bytes leyo Trino para ejecutar el query de Gold? ¿Y para el query de Silver?
¿Por que Gold es mas eficiente?

---

## Reto opcional 1: Crear una vista en Trino

```sql
-- Crear una vista sobre Silver con las ventas de Bogota
CREATE VIEW ventas_bogota AS
SELECT id, fecha, producto, cantidad, total, ganancia
FROM silver_ventas
WHERE region = 'Bogota';

-- Consultar la vista
SELECT * FROM ventas_bogota ORDER BY total DESC LIMIT 10;
```

---

## Reto opcional 2: Comparar Gold vs consulta directa sobre Silver

Ejecuta el query de ingresos por region directamente sobre Silver:

```sql
SELECT region,
       ROUND(SUM(total), 2)    AS ingresos_totales,
       COUNT(*)                 AS num_transacciones
FROM silver_ventas
GROUP BY region
ORDER BY ingresos_totales DESC;
```

Compara el resultado con la consulta equivalente sobre Gold.
¿Son identicos? ¿Cual fue mas rapido? ¿Por que existe Gold si podemos agregar Silver en tiempo real?

---

## Preguntas de reflexion

1. **¿Por que Trino puede leer las tablas de Iceberg sin necesitar Spark?**
   Explica el rol del catalogo REST en este proceso. ¿Que informacion obtiene Trino del catalogo?

2. **¿Que rol juega el catalogo REST entre Spark y Trino?**
   ¿Que pasaria si Spark escribiera las tablas sin registrarlas en un catalogo compartido?

3. **¿En que caso usarias Trino en lugar de Spark SQL?**
   Menciona al menos dos escenarios donde Trino es la mejor opcion y dos donde Spark lo es.

4. **Sobre el query plan de Trino UI**: ¿que significa que un query tenga multiples "stages"?
   ¿Como se distribuye el trabajo cuando hay un `GROUP BY`?

---

## Evidencia minima del curso completo

Ademas de las capturas de este lab, escribe un parrafo breve (5-8 oraciones) respondiendo:

**"¿Que camino recorrimos desde el Taller 2 hasta el Taller 6?"**

Debe mencionar:
- La evolucion del storage (HDFS → MinIO/S3).
- La evolucion del motor de procesamiento (MapReduce → Spark).
- La evolucion del formato de datos (texto plano → Parquet → Iceberg).
- Por que cada cambio fue necesario o ventajoso.
- Que agrega el Lakehouse (T6) que no teniamos en los talleres anteriores.

---

## Cierre: progresion de los 5 talleres

| Taller | Storage      | Engine          | Formato   | Concepto clave                          |
|--------|--------------|-----------------|-----------|-----------------------------------------|
| T2     | HDFS         | MapReduce       | Text/CSV  | Procesamiento distribuido basico        |
| T3     | HDFS         | Spark           | Text/CSV  | Spark como reemplazo de MapReduce       |
| T4     | HDFS / local | Spark           | Parquet   | Formatos columnar y DataFrames          |
| T5     | MinIO (S3)   | Spark           | Iceberg   | Open table formats, snapshots, schema   |
| T6     | MinIO (S3)   | Spark + Trino   | Iceberg   | Lakehouse: capas, catalogo compartido   |
