#!/usr/bin/env python3
"""Transformacion a capa Silver — Taller 6 Lakehouse.

Lee Bronze, limpia datos, hace join con dimensiones de productos,
calcula total y ganancia por transaccion.
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

DIM_PATH = "/home/iceberg/data/dimensiones_productos.csv"

spark = (
    SparkSession.builder
    .appName("Transform-Silver")
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
    .config("spark.sql.catalog.demo", "org.apache.iceberg.spark.SparkCatalog")
    .config("spark.sql.catalog.demo.type", "rest")
    .config("spark.sql.catalog.demo.uri", "http://rest:8181")
    .config("spark.sql.catalog.demo.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")
    .config("spark.sql.catalog.demo.warehouse", "s3://warehouse/")
    .config("spark.sql.catalog.demo.s3.endpoint", "http://minio:9000")
    .config("spark.sql.defaultCatalog", "demo")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

# --- Leer Bronze ---
print("Leyendo capa Bronze...")
bronze = spark.sql("SELECT * FROM demo.lakehouse.bronze_ventas")
raw_count = bronze.count()
print(f"  Registros en Bronze: {raw_count}")

# --- Limpiar datos ---
clean = (
    bronze
    .dropna(subset=["id", "fecha", "producto", "cantidad", "precio_unitario", "region"])
    .filter(F.col("cantidad") > 0)
    .filter(F.col("precio_unitario") > 0)
)
clean_count = clean.count()
dropped = raw_count - clean_count
print(f"  Registros validos: {clean_count}  (eliminados por limpieza: {dropped})")

# --- Join con dimensiones ---
print("Cargando dimensiones de productos...")
dim = spark.read.csv(DIM_PATH, header=True, inferSchema=True)

enriched = (
    clean
    .join(dim.select("producto", "proveedor", "margen_pct"), on="producto", how="left")
)

# --- Calcular metricas de transaccion ---
silver = (
    enriched
    .withColumn("total", F.round(F.col("cantidad") * F.col("precio_unitario"), 2))
    .withColumn("ganancia", F.round(F.col("total") * F.col("margen_pct"), 2))
    .withColumn("silver_ts", F.current_timestamp())
)

# --- Escribir Silver ---
silver.writeTo("demo.lakehouse.silver_ventas").createOrReplace()

count = spark.sql("SELECT COUNT(*) AS total FROM demo.lakehouse.silver_ventas").collect()[0][0]
print(f"\nSilver: {count} filas escritas exitosamente.")
print("\nMuestra Silver (columnas clave):")
spark.sql("""
    SELECT id, fecha, producto, proveedor, categoria, cantidad,
           precio_unitario, total, margen_pct, ganancia, region
    FROM demo.lakehouse.silver_ventas
    LIMIT 5
""").show()

spark.stop()
