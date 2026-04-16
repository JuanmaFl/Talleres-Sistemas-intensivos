#!/usr/bin/env python3
"""Ingestión a capa Bronze — Taller 6 Lakehouse."""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

DATA_PATH = "/home/iceberg/data/ventas_lote1.csv"

spark = (
    SparkSession.builder
    .appName("Ingest-Bronze")
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

spark.sql("CREATE NAMESPACE IF NOT EXISTS demo.lakehouse")

df = spark.read.csv(DATA_PATH, header=True, inferSchema=True)

df = (
    df
    .withColumn("ingestion_ts", F.current_timestamp())
    .withColumn("source_file", F.lit("ventas_lote1.csv"))
)

df.writeTo("demo.lakehouse.bronze_ventas").createOrReplace()

count = spark.sql("SELECT COUNT(*) AS total FROM demo.lakehouse.bronze_ventas").collect()[0][0]
print(f"\nBronze: {count} filas ingestadas exitosamente.")
print("\nMuestra de los primeros 5 registros:")
spark.sql("SELECT * FROM demo.lakehouse.bronze_ventas LIMIT 5").show()

spark.stop()
