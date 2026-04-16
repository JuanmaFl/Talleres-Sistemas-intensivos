#!/usr/bin/env python3
"""Transformacion a capa Gold — Taller 6 Lakehouse.

Lee Silver, agrega metricas de negocio por region y mes,
escribe tabla Gold lista para consumo analitico.
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (
    SparkSession.builder
    .appName("Transform-Gold")
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

# --- Leer Silver ---
print("Leyendo capa Silver...")
silver = spark.sql("SELECT * FROM demo.lakehouse.silver_ventas")
print(f"  Registros en Silver: {silver.count()}")

# --- Agregar metricas por region y mes ---
gold = (
    silver
    .withColumn("anio", F.year(F.col("fecha").cast("date")))
    .withColumn("mes", F.month(F.col("fecha").cast("date")))
    .withColumn("anio_mes", F.date_format(F.col("fecha").cast("date"), "yyyy-MM"))
    .groupBy("region", "categoria", "anio", "mes", "anio_mes")
    .agg(
        F.round(F.sum("total"), 2).alias("ingresos_totales"),
        F.round(F.sum("ganancia"), 2).alias("ganancia_total"),
        F.count("id").alias("num_transacciones"),
        F.round(F.avg("total"), 2).alias("ticket_promedio"),
        F.sum("cantidad").alias("unidades_vendidas"),
    )
    .withColumn("gold_ts", F.current_timestamp())
    .orderBy("region", "anio", "mes", "categoria")
)

# --- Escribir Gold ---
gold.writeTo("demo.lakehouse.gold_metricas_region").createOrReplace()

count = spark.sql("SELECT COUNT(*) AS total FROM demo.lakehouse.gold_metricas_region").collect()[0][0]
print(f"\nGold: {count} filas de metricas generadas.")
print("\nMetricas por region:")
spark.sql("""
    SELECT region,
           SUM(ingresos_totales)   AS ingresos_totales,
           SUM(ganancia_total)     AS ganancia_total,
           SUM(num_transacciones)  AS num_transacciones,
           SUM(unidades_vendidas)  AS unidades_vendidas
    FROM demo.lakehouse.gold_metricas_region
    GROUP BY region
    ORDER BY ingresos_totales DESC
""").show()

spark.stop()
