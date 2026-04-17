# jobs/analisis_completo.py - Report final
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, avg, count, when
from datetime import datetime

spark = SparkSession.builder \
    .appName("AnalisisCompleto") \
    .master("local[*]") \
    .config("spark.driver.host", "127.0.0.1") \
    .getOrCreate()

df = spark.read.parquet("/tmp/ventas_processed.parquet")
df.createOrReplaceTempView("ventas")

print("=" * 60)
print(f"REPORTE FINAL TALLER 4 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 60)

# 1. Resumen general
print("\n1. RESUMEN GENERAL")
print("-" * 60)
stats = df.agg(
    count("id").alias("total_transacciones"),
    sum("cantidad").alias("cantidad_total"),
    sum("total").alias("ingresos_totales"),
    avg("total").alias("ingresos_promedio")
).collect()[0]

print(f"Total transacciones: {stats['total_transacciones']}")
print(f"Cantidad total vendida: {stats['cantidad_total']}")
print(f"Ingresos totales: ${stats['ingresos_totales']:,.0f}")
print(f"Ingresos promedio/venta: ${stats['ingresos_promedio']:,.0f}")

# 2. Por región
print("\n2. DESEMPEÑO POR REGIÓN")
print("-" * 60)
spark.sql("""
    SELECT region, 
           COUNT(*) as ventas,
           SUM(total) as ingresos,
           ROUND(AVG(total), 2) as promedio
    FROM ventas
    GROUP BY region
    ORDER BY ingresos DESC
""").show()

# 3. Por categoría
print("\n3. DESEMPEÑO POR CATEGORÍA")
print("-" * 60)
spark.sql("""
    SELECT categoria,
           COUNT(*) as num_ventas,
           SUM(cantidad) as unidades,
           SUM(total) as ingresos
    FROM ventas
    GROUP BY categoria
    ORDER BY ingresos DESC
""").show()

# 4. Top 10 ventas
print("\n4. TOP 10 MAYORES VENTAS")
print("-" * 60)
spark.sql("""
    SELECT id, fecha, producto, categoria, cantidad, 
           precio_unitario, region, total
    FROM ventas
    ORDER BY total DESC
    LIMIT 10
""").show(truncate=False)

# 5. Estadísticas de precio
print("\n5. ESTADÍSTICAS DE PRECIO")
print("-" * 60)
spark.sql("""
    SELECT categoria,
           MIN(precio_unitario) as precio_min,
           AVG(precio_unitario) as precio_promedio,
           MAX(precio_unitario) as precio_max
    FROM ventas
    GROUP BY categoria
    ORDER BY precio_promedio DESC
""").show()

print("\n" + "=" * 60)
print("FIN DEL REPORTE")
print("=" * 60)

spark.stop()