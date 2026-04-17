# jobs/lab2_dataframe_api.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, avg, count, when

spark = SparkSession.builder \
    .appName("Lab2-DataFrameAPI") \
    .master("local[*]") \
    .config("spark.driver.host", "127.0.0.1") \
    .getOrCreate()

# Leer CSV
df = spark.read.csv("/data/ventas.csv", header=True, inferSchema=True)

print("=== DataFrame original ===")
df.show(3)
df.printSchema()

# Lab 2.1: withColumn - calcular total por venta
df_with_total = df.withColumn("total", col("cantidad") * col("precio_unitario"))
print("\n=== Con columna 'total' ===")
df_with_total.select("id", "producto", "cantidad", "precio_unitario", "total").show(5)

# Lab 2.2: groupBy + agg - ventas por región
print("\n=== Ventas por región ===")
df_with_total.groupBy("region") \
    .agg(
        count("id").alias("num_ventas"),
        sum("cantidad").alias("total_cantidad"),
        sum("total").alias("total_ingresos"),
        avg("total").alias("promedio_venta")
    ) \
    .orderBy(col("total_ingresos").desc()) \
    .show()

# Lab 2.3: groupBy + agg - ventas por categoría
print("\n=== Ventas por categoría ===")
df_with_total.groupBy("categoria") \
    .agg(
        count("id").alias("num_transacciones"),
        sum("cantidad").alias("cantidad_vendida"),
        avg("precio_unitario").alias("precio_promedio")
    ) \
    .orderBy(col("cantidad_vendida").desc()) \
    .show()

# Lab 2.4: withColumn con condición - marcar ventas altas
print("\n=== Marcar ventas >= 3M ===")
df_flagged = df_with_total.withColumn(
    "venta_alta", 
    when(col("total") >= 3000000, "Si").otherwise("No")
)
df_flagged.select("id", "producto", "total", "venta_alta").show(10)

spark.stop()