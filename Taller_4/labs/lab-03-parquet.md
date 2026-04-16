# Lab 3: Escribir y leer en formato Parquet

## Objetivo

Entender las ventajas del formato columnar Parquet frente a CSV: compresion,
lectura selectiva de columnas (column pruning) y predicados empujados al lector
(predicate pushdown).

---

## Contexto rapido

**CSV** es un formato por filas: para leer una sola columna hay que leer cada
fila completa. En un dataset con 100 columnas y millones de filas eso es un
desperdicio masivo de I/O.

**Parquet** almacena los datos por columnas contiguas en disco. Si tu consulta
solo necesita `region` y `total`, Spark lee unicamente esos bytes. Ademas, Parquet
incluye estadisticas por bloque (min, max) que permiten saltarse bloques enteros
cuando hay un filtro (predicate pushdown).

---

## Pasos

### 1. Escribir el DataFrame en Parquet

Asegurate de tener el DataFrame `df` del Lab 2 (con la columna `total`):

```python
PARQUET_PATH = "/tmp/ventas_parquet"

df.write.mode("overwrite").parquet(PARQUET_PATH)
print("Escritura completada.")
```

### 2. Leer de vuelta el Parquet y verificar el schema

```python
df_parquet = spark.read.parquet(PARQUET_PATH)
df_parquet.printSchema()
df_parquet.show(5)
print("Filas:", df_parquet.count())
```

Observa que el schema (tipos de dato) se preservo exactamente, sin necesidad de
`inferSchema`. Parquet lleva el schema embebido en el archivo.

### 3. Comparar tamanos

En una celda de Jupyter puedes ejecutar comandos de shell con `!`:

```bash
!du -sh /home/jovyan/data/ventas.csv
!du -sh /tmp/ventas_parquet/
```

Con 50 filas el CSV es mas pequeno que el directorio Parquet (que incluye metadata
y encabezados de columna). La ventaja de Parquet se hace evidente a partir de
miles de filas y especialmente cuando hay muchas columnas.

### 4. Leer solo una columna del Parquet (column pruning)

```python
# Solo la columna "total" — Spark no lee las demas del disco
solo_total = spark.read.parquet(PARQUET_PATH).select("total")
solo_total.show(5)
```

Compara con leer todo el CSV y luego seleccionar:

```python
todo_csv = spark.read.csv(
    "/data/ventas.csv", header=True, inferSchema=True
).select("total")
todo_csv.show(5)
```

Usa `explain()` en ambos casos para ver la diferencia en el plan fisico:

```python
solo_total.explain()
todo_csv.explain()
```

En el plan del Parquet deberia aparecer `PartitionFilters` y las columnas
leidas deberian ser solo las seleccionadas.

---

## Que es column pruning

Cuando Spark lee Parquet y sabe que solo necesita ciertas columnas, descarta las
demas antes de cargarlas en memoria. Esto se llama **column pruning** (poda de
columnas). Es automatico; el desarrollador no tiene que hacer nada especial.

## Que es predicate pushdown

Si tienes un filtro como `WHERE region = 'Bogota'`, Spark puede pasarle ese
predicado directamente al lector de Parquet. El lector evalua las estadisticas
de cada bloque (row group) y salta los que no pueden contener `region = 'Bogota'`.
Resultado: menos datos leidos del disco antes de llegar a Spark.

---

## Preguntas

1. **¿Por que Parquet es mas eficiente que CSV para consultas analiticas que
   solo usan 2 o 3 columnas de un dataset con muchas columnas?**

2. **¿Que pasa si solo necesitas las columnas `region` y `total` de un archivo
   CSV con 100 columnas y 10 millones de filas?**

3. **¿Por que el directorio Parquet contiene varios archivos en lugar de uno solo?**
   (pista: tiene que ver con el numero de particiones del DataFrame)

---

## Evidencia minima

- Salida de `du -sh` para el CSV y el directorio Parquet.
- Captura del schema leido desde Parquet (sin `inferSchema`).
- Salida de `explain()` para la lectura selectiva de columnas.
