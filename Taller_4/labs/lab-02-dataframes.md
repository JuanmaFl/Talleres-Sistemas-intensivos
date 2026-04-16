# Lab 2: Explorar el dataset con DataFrames

## Objetivo

Entender la API de DataFrames de Spark: leer datos estructurados desde CSV,
inspeccionar el schema, aplicar transformaciones y calcular agregaciones.

---

## Pasos

### 1. Leer el CSV

En el notebook (continuando desde Lab 1, o con una nueva SparkSession):

```python
df = spark.read.csv("/data/ventas.csv", header=True, inferSchema=True)
```

### 2. Inspeccionar el schema y los datos

```python
# Schema inferido por Spark
df.printSchema()

# Primeras 5 filas
df.show(5)

# Total de filas
print("Total filas:", df.count())
```

Observa los tipos de dato que Spark asigno a cada columna. Presta atencion a
`fecha` (deberia ser `DateType` o `TimestampType`), `cantidad` (`IntegerType`) y
`precio_unitario` (`IntegerType` o `LongType`).

### 3. Agregar la columna `total`

```python
from pyspark.sql import functions as F

df = df.withColumn("total", F.col("cantidad") * F.col("precio_unitario"))
df.show(5)
```

### 4. Filtrar ventas de Bogota mayores a 500 000

```python
df_bogota = df.filter(
    (F.col("region") == "Bogota") & (F.col("total") > 500_000)
)
df_bogota.show()
print("Ventas en Bogota > 500 000:", df_bogota.count())
```

### 5. Agrupar por region y calcular metricas

```python
resumen = (
    df.groupBy("region")
    .agg(
        F.sum("total").alias("ingresos_totales"),
        F.count("id").alias("num_transacciones"),
        F.avg("total").alias("ticket_promedio")
    )
    .orderBy(F.desc("ingresos_totales"))
)
resumen.show()
```

### 6. Ver el plan de ejecucion (opcional pero recomendado)

```python
resumen.explain()
```

Esto muestra como Spark planifica las operaciones internamente antes de ejecutarlas.

---

## Preguntas

1. **¿Que es `inferSchema=True` y que ocurre si no lo usas?**
   Prueba leer el CSV sin ese parametro y compara el schema resultante.

2. **¿Que tipo de dato le asigno Spark a la columna `fecha`? ¿Por que importa
   el tipo correcto para hacer calculos por mes?**

3. **¿En que se diferencia un DataFrame de Spark de un DataFrame de pandas?**
   Piensa en donde viven los datos, quien ejecuta las operaciones y como se
   maneja la memoria.

4. **¿Cual es la region con mayores ingresos totales? ¿Y la que tiene el ticket
   promedio mas alto?**

---

## Evidencia minima

- Captura de `df.printSchema()` mostrando los tipos inferidos.
- Tabla de la agrupacion por region con las tres metricas calculadas.
