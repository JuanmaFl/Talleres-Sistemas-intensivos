# Lab 4: Comparacion y analisis

## Objetivo

Ejecutar `make compare` para correr ambos engines en secuencia y obtener una tabla de tiempos comparable. Analizar las diferencias de codigo, rendimiento y conceptos entre MapReduce y Spark.

## Pasos

### 1. Ejecutar la comparacion completa

```bash
make compare
```

Este comando ejecuta ambos jobs en secuencia (primero MapReduce, luego Spark) sobre los mismos datos y muestra una tabla al final:

```
==========================================
  COMPARACION DE TIEMPOS - WORDCOUNT
==========================================
  MapReduce :  XXs
  Spark     :  XXs
==========================================
  Spark fue ~Xx mas rapido en este dataset.
==========================================
```

Anota los tiempos:

| Engine | Tiempo (segundos) |
|--------|-------------------|
| MapReduce | |
| Spark | |
| Factor | |

### 2. Analizar el codigo: MapReduce vs PySpark

Abre `jobs/wordcount.py` y compara con la descripcion del WordCount en Java que aparece en `docs/architecture.md`.

Cuenta las lineas de logica real (sin contar imports, docstrings ni lineas en blanco) en cada version.

| Aspecto | MapReduce (Java) | Spark (PySpark) |
|---------|-----------------|-----------------|
| Lineas de logica | ~60 | ~12 |
| Clases necesarias | 3 (Mapper, Reducer, Driver) | 0 (funciones lambda) |
| Configuracion del job | ~15 lineas | 6 lineas (SparkSession) |
| Logica del algoritmo | Separada en 2 metodos | Una cadena de transformaciones |

### 3. Comparar los outputs

Verifica que ambos outputs contengan las mismas palabras con los mismos conteos:

```bash
# Ver top palabras de MapReduce
docker compose exec -T namenode bash -c \
  "hdfs dfs -cat /user/root/wordcount/output-mr/part-r-00000 | sort -k2 -rn | head -n 10"

# Ver top palabras de Spark (puede estar en varios part files)
docker compose exec -T namenode bash -c \
  "hdfs dfs -cat /user/root/wordcount/output-spark/part-* | sort -k2 -rn | head -n 10"
```

¿Son identicos los conteos?

## Preguntas de analisis

### Preguntas sobre los resultados

1. **Orden de palabras con el mismo conteo**: Si dos palabras tienen exactamente el mismo numero de ocurrencias, ¿por que el orden de esas palabras puede ser diferente entre el output de MapReduce y el de Spark? (Pista: piensa en como cada engine maneja el tie-breaking en el ordenamiento.)

2. **Dataset pequeno**: ¿Por que con un dataset de pocos kilobytes la diferencia de tiempo puede ser modesta o incluso negativa para Spark? Nombra al menos dos fuentes de overhead fijo en Spark que no dependen del volumen de datos.

3. **Cuando MapReduce sigue siendo valido**: ¿En que escenarios especificos MapReduce podria seguir siendo la mejor opcion frente a Spark? Considera factores como tolerancia a fallos, costo de RAM, tamano del dataset vs memoria del cluster.

4. **Limitacion de RDDs vs DataFrames**: Este wordcount usa la API de RDDs de Spark (la mas de bajo nivel). ¿Que limitacion tiene comparado con hacer el mismo calculo usando DataFrames de Spark SQL? (Pista: piensa en el optimizador Catalyst y en la legibilidad del codigo.)

### Preguntas de profundizacion

5. Si agregaras 100 archivos de texto de 10 MB cada uno y re-corrieras `make compare`, ¿esperarias ver una diferencia mayor o menor en el factor de velocidad? ¿Por que?

6. El script de MapReduce escribe los resultados intermedios del shuffle en disco local de los NodeManagers. ¿Que pasaria si un NodeManager falla durante el shuffle? ¿Como maneja ese caso MapReduce? ¿Como lo maneja Spark?

7. En el codigo PySpark, la llamada `sortBy` ocurre antes de `saveAsTextFile`. ¿Eso significa que Spark ordena los datos antes de guardarlos? ¿O el ordenamiento es parte del mismo job de escritura? Explica la respuesta usando el concepto de lazy evaluation.

## Retos opcionales

### Reto 1: Dataset mas grande

Agrega mas archivos de texto al directorio `data/wordcount/` (pueden ser articulos de Wikipedia en texto plano, libros de Project Gutenberg, etc.) y vuelve a correr `make compare`. ¿Como cambia el factor de velocidad?

```bash
# Ejemplo: descargar un texto de Project Gutenberg
curl -o data/wordcount/quijote.txt \
  "https://www.gutenberg.org/cache/epub/2000/pg2000.txt"
make compare
```

### Reto 2: Ajustar recursos de Spark

En `docker-compose.yml`, cambia `SPARK_WORKER_CORES` de `2` a `1` en ambos workers y vuelve a correr `make compare`. ¿Que impacto tiene reducir los cores disponibles en el tiempo de Spark vs el tiempo de MapReduce?

### Reto 3: Analizar el shuffle

En Spark UI, busca la metrica **Shuffle Read** y **Shuffle Write** en los stages de la ultima ejecucion. Compara esos numeros con los contadores `FILE_BYTES_WRITTEN` del job MapReduce en JobHistory Server. ¿Que conclusiones puedes sacar sobre la cantidad de datos que cada engine mueve durante el shuffle?

## Evidencia minima

- Captura de pantalla de la tabla de tiempos producida por `make compare`.
- Tabla de comparacion de codigo (lineas, clases) completa con tus observaciones.
- Respuestas a las cuatro preguntas de analisis principales (preguntas 1 a 4).
