# Lab 4: Spark SQL y analisis final

## Objetivo

Usar SQL como interfaz de alto nivel sobre los datos Parquet. Spark SQL permite
escribir consultas familiares sobre DataFrames sin cambiar de herramienta, y el
optimizador (Catalyst) aplica las mismas mejoras que con la DataFrame API.

---

## Pasos

### 1. Registrar el DataFrame Parquet como TempView

```python
PARQUET_PATH = "/tmp/ventas_parquet"
df_parquet = spark.read.parquet(PARQUET_PATH)

df_parquet.createOrReplaceTempView("ventas")
print("TempView 'ventas' registrada.")
```

### 2. Ventas totales por categoria y mes

```python
spark.sql("""
    SELECT
        categoria,
        month(fecha) AS mes,
        SUM(cantidad * precio_unitario) AS ingresos
    FROM ventas
    GROUP BY categoria, mes
    ORDER BY mes, ingresos DESC
""").show()
```

### 3. Top 3 productos por region

```python
spark.sql("""
    SELECT region, producto, ingresos
    FROM (
        SELECT
            region,
            producto,
            SUM(cantidad * precio_unitario) AS ingresos,
            RANK() OVER (PARTITION BY region ORDER BY SUM(cantidad * precio_unitario) DESC) AS ranking
        FROM ventas
        GROUP BY region, producto
    )
    WHERE ranking <= 3
    ORDER BY region, ranking
""").show(20)
```

### 4. Ratio cantidad / precio_unitario promedio por region

```python
spark.sql("""
    SELECT
        region,
        ROUND(AVG(CAST(cantidad AS DOUBLE) / precio_unitario), 8) AS ratio_cant_precio
    FROM ventas
    GROUP BY region
    ORDER BY ratio_cant_precio DESC
""").show()
```

### 5. Guardar el resultado final como Parquet

```python
resultado_final = spark.sql("""
    SELECT
        categoria,
        month(fecha) AS mes,
        region,
        SUM(cantidad * precio_unitario) AS ingresos,
        COUNT(*) AS transacciones
    FROM ventas
    GROUP BY categoria, mes, region
    ORDER BY mes, ingresos DESC
""")

RESULTADO_PATH = "/tmp/resultado_final"
resultado_final.write.mode("overwrite").parquet(RESULTADO_PATH)
print(f"Resultado guardado en: {RESULTADO_PATH}")
resultado_final.show(20)
```

---

## Retos opcionales

Si terminas antes que el grupo, intenta estas consultas adicionales:

### Reto 1: Variacion mensual de ingresos

Calcula cuanto crecieron (o cayeron) los ingresos totales de un mes al siguiente.
Pista: usa `LAG(ingresos) OVER (ORDER BY mes)`.

### Reto 2: Region con mayor crecimiento

Identifica que region tuvo el mayor incremento porcentual de ingresos entre
enero y el mes con mejores ventas.

### Reto 3: Producto mas vendido por mes

Para cada mes, cual fue el producto que mas unidades vendio.

---

## Preguntas

1. **¿Que ventaja tiene Spark SQL sobre la DataFrame API para un analista de datos
   que ya sabe SQL pero no sabe Python?**

2. **¿Que es un TempView y por que no persiste entre sesiones de Spark?**
   Si el kernel de Jupyter se reinicia, ¿que pasa con la TempView?

3. **¿Podrias hacer la misma consulta del paso 3 (Top 3 por region) usando
   solo la DataFrame API (sin SQL)? ¿Cual te parece mas legible?**

4. **En el paso 5 guardas el resultado en Parquet. ¿Por que tiene sentido guardar
   resultados intermedios en Parquet en lugar de re-calcularlos cada vez?**

---

## Evidencia minima

- Salida del query de ventas por categoria y mes (paso 2).
- Salida del top 3 productos por region (paso 3).
- Confirmacion de escritura del resultado final en `/tmp/resultado_final`.
