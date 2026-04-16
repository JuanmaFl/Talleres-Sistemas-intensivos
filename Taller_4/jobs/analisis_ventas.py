#!/usr/bin/env python3
"""Analisis de ventas con Spark DataFrames — referencia del Taller 4."""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

DATA_PATH    = "/data/ventas.csv"
PARQUET_PATH = "/tmp/ventas_parquet"


def main():
    spark = (
        SparkSession.builder
        .appName("AnalisisVentas")
        .master("spark://spark-master:7077")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    # Cargar CSV
    df = spark.read.csv(DATA_PATH, header=True, inferSchema=True)
    print("=== Schema inferido ===")
    df.printSchema()

    # Transformacion: columna total
    df = df.withColumn("total", F.col("cantidad") * F.col("precio_unitario"))

    # Agregacion por region
    print("\n=== Ventas por region ===")
    df.groupBy("region") \
      .agg(
          F.sum("total").alias("ingresos_totales"),
          F.count("id").alias("num_transacciones"),
          F.avg("total").alias("ticket_promedio")
      ) \
      .orderBy(F.desc("ingresos_totales")) \
      .show()

    # Top 5 productos
    print("\n=== Top 5 productos por ingresos ===")
    df.groupBy("producto") \
      .agg(F.sum("total").alias("ingresos")) \
      .orderBy(F.desc("ingresos")) \
      .limit(5) \
      .show()

    # Guardar como Parquet
    df.write.mode("overwrite").parquet(PARQUET_PATH)
    print(f"\nDatos guardados en Parquet: {PARQUET_PATH}")

    # Releer Parquet y mostrar diferencia de tamano (comparacion conceptual)
    df_parquet = spark.read.parquet(PARQUET_PATH)
    print(f"\nFilas en Parquet: {df_parquet.count()}")

    # Spark SQL
    df_parquet.createOrReplaceTempView("ventas")
    print("\n=== Spark SQL: ventas por categoria y mes ===")
    spark.sql("""
        SELECT
            categoria,
            month(fecha) AS mes,
            SUM(cantidad * precio_unitario) AS ingresos
        FROM ventas
        GROUP BY categoria, mes
        ORDER BY mes, ingresos DESC
    """).show()

    spark.stop()


if __name__ == "__main__":
    main()
