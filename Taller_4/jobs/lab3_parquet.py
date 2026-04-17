# jobs/lab3_parquet.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, avg

spark = SparkSession.builder \
    .appName("Lab3-Parquet") \
    .master("local[*]") \
    .config("spark.driver.host", "127.0.0.1") \
    .getOrCreate()

# Leer CSV
df = spark.read.csv("/data/ventas.csv", header=True, inferSchema=True)
df_with_total = df.withColumn("total", col("cantidad") * col("precio_unitario"))

# Lab 3.1: Escribir a Parquet
parquet_path = "/tmp/ventas_processed.parquet" 
print(f"Escribiendo a {parquet_path}...")
df_with_total.write.mode("overwrite").parquet(parquet_path)
print("✓ Escritura completada")

# Lab 3.2: Leer de Parquet
print("\nLeyendo de Parquet...")
df_parquet = spark.read.parquet(parquet_path)
print(f"✓ Lectura completada: {df_parquet.count()} registros")

# Lab 3.3: Column Pruning (leer solo columnas necesarias)
print("\n=== Column Pruning: solo región y total ===")
df_pruned = spark.read.parquet(parquet_path).select("region", "total")
df_pruned.show(5)

# Lab 3.4: Predicate Pushdown (filtrar antes de leer)
print("\n=== Predicate Pushdown: ventas > 2M ===")
df_filtered = spark.read.parquet(parquet_path).filter(col("total") > 2000000)
print(f"Registros con total > 2M: {df_filtered.count()}")
df_filtered.select("id", "producto", "region", "total").show()

# Lab 3.5: Aggregación sobre Parquet
print("\n=== Agregación sobre Parquet ===")
spark.read.parquet(parquet_path) \
    .groupBy("categoria") \
    .agg(
        sum("total").alias("ingresos_totales"),
        avg("total").alias("ingresos_promedio")
    ) \
    .orderBy(col("ingresos_totales").desc()) \
    .show()

spark.stop()