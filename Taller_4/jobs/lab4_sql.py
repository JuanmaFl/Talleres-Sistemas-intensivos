# jobs/lab4_sql.py
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Lab4-SparkSQL") \
    .master("local[*]") \
    .config("spark.driver.host", "127.0.0.1") \
    .getOrCreate()

# Leer Parquet (creado en Lab 3)
df = spark.read.parquet("/tmp/ventas_processed.parquet")

# Lab 4.1: Crear TempView
df.createOrReplaceTempView("ventas")
print("✓ TempView 'ventas' creado")

# Lab 4.2: Queries SQL básicas
print("\n=== Top 5 ventas por monto ===")
spark.sql("""
    SELECT id, producto, categoria, total, region
    FROM ventas
    ORDER BY total DESC
    LIMIT 5
""").show()

# Lab 4.3: Agregación con GROUP BY
print("\n=== Ingresos totales por región ===")
spark.sql("""
    SELECT region, 
           COUNT(*) as num_ventas,
           SUM(cantidad) as cantidad_total,
           SUM(total) as ingresos_totales,
           AVG(total) as promedio_venta
    FROM ventas
    GROUP BY region
    ORDER BY ingresos_totales DESC
""").show()

# Lab 4.4: Agregación con HAVING
print("\n=== Categorías con ingresos > 5M ===")
spark.sql("""
    SELECT categoria,
           COUNT(*) as num_transacciones,
           SUM(total) as total_ingresos
    FROM ventas
    GROUP BY categoria
    HAVING SUM(total) > 5000000
    ORDER BY total_ingresos DESC
""").show()

# Lab 4.5: JOIN simulado (categoría en subconsulta)
print("\n=== Top 3 productos por región ===")
spark.sql("""
    WITH ranked_ventas AS (
        SELECT region, producto, categoria, total,
               ROW_NUMBER() OVER (PARTITION BY region ORDER BY total DESC) as rn
        FROM ventas
    )
    SELECT region, producto, categoria, total
    FROM ranked_ventas
    WHERE rn <= 3
    ORDER BY region, total DESC
""").show(20)

# Lab 4.6: Guardar resultado a CSV
output_path = "/data/resumen_ventas.csv"
print(f"\nGuardando resumen a {output_path}...")
spark.sql("""
    SELECT region, 
           SUM(total) as ingresos_totales,
           COUNT(*) as num_ventas,
           AVG(precio_unitario) as precio_promedio
    FROM ventas
    GROUP BY region
    ORDER BY ingresos_totales DESC
""").write.mode("overwrite").csv(output_path, header=True)
print("✓ Guardado completado")

spark.stop()