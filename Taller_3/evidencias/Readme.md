# Evidencias - Taller 3: De MapReduce a Spark

**Equipo:** Samuel Molina, David Felipe Rios, Juan Manuel Flórez  
**Curso:** Sistemas Intensivos de Datos  
**Universidad:** EAFIT  
**Fecha:** 16-17 de Abril de 2026

---

## Descripción General

Este taller comparó MapReduce y Spark ejecutando el mismo problema de wordcount en un cluster Hadoop distribuido. Procesamos 4 archivos de texto (~2KB) describiendo conceptos de big data y contamos palabras para ver cómo cada framework las maneja.

---

## Capturas de Evidencia

### 01-cluster-status.png
**¿Qué es?** Salida del comando `docker compose ps` mostrando el estado de los 10 contenedores.

**Lo que ves:**
- 7 contenedores Hadoop: namenode, 2 datanodes, resourcemanager, 2 nodemanagers, historyserver
- 3 contenedores Spark: spark-master y 2 workers
- Todos con estado "Up" y healthy

**Por qué importa:** Sin estos 10 contenedores corriendo correctamente, el cluster no funciona. Esta imagen prueba que el setup inicial fue exitoso.

---

### 02-hdfs-data-load.png
**¿Qué es?** Salida de `hdfs dfs -ls /user/root/wordcount/input/` listando los archivos en el sistema de archivos distribuido.

**Lo que ves:**
- hdfs.txt (408 bytes)
- introduccion.txt (391 bytes)
- mapreduce.txt (535 bytes)
- spark.txt (646 bytes)
- Total: ~2 KB

**Por qué importa:** Confirma que los datos están en HDFS listo para que MapReduce y Spark los procesen.

---

### 03-mapreduce-execution.png
**¿Qué es?** Salida del comando que ejecuta el jar de MapReduce para contar palabras.

**Lo que ves:**
- 4 mappers procesando en paralelo (uno por archivo)
- 1 reducer consolidando resultados
- Tiempo: ~43 segundos (con overhead de setup del cluster)
- "Map input records: 23" (líneas procesadas)
- "map 100% reduce 100%" confirmando completitud

**Por qué importa:** Muestra que MapReduce ejecutó correctamente y da una línea base de tiempo para comparar contra Spark.

---

### 04-mapreduce-output.txt
**¿Qué es?** Salida de `hdfs dfs -cat /user/root/wordcount/output-mr/part-r-00000` mostrando el resultado del wordcount de MapReduce.

**Lo que ves:**
- 182 palabras únicas encontradas
- Top palabras: "de" (21), "el" (14), "y" (13), "en" (11)
- Formato: palabra<tab>conteo

**Por qué importa:** Este es el resultado que usamos para validar que Spark produce exactamente lo mismo.

---

### 05-spark-execution.png (image.png)
**¿Qué es?** Salida de `spark-submit /tmp/wordcount.py` ejecutando el mismo wordcount en Spark.

**Lo que ves:**
```
=== Top 30 palabras (Spark) ===
de      21
el      14
y       13
en      11
la      9
los     9
es      8
spark   8
mapreduce       6
datos   6
para    6
...
```

**Por qué importa:** Los resultados son **idénticos** a MapReduce, pero se ejecutó en ~12 segundos vs 43 segundos. Esto demuestra la ventaja de velocidad de Spark.

---

## Proceso Paso a Paso

### Fase 1: Setup del Cluster
Levantamos 10 contenedores Docker con Hadoop y Spark usando `docker-compose up -d`. Esto tomó unos minutos y requería que todos los servicios se inicializaran correctamente.

### Fase 2: Cargar Datos a HDFS
Copiamos 4 archivos de texto al namenode y los pusimos en HDFS usando `hdfs dfs -put`. Verificamos con `hdfs dfs -ls` que los datos estaban ahí.

### Fase 3: Ejecutar MapReduce
Lanzamos el jar de wordcount de Hadoop sobre los datos. El framework creó 4 mappers (uno por archivo) que procesaron el texto en paralelo, luego un reducer agregó los conteos. Tomó ~43 segundos.

### Fase 4: Ejecutar Spark
Creamos un script PySpark que leía los mismos datos, hacía flatMap para dividir en palabras, limpiaba puntuación, contaba con reduceByKey y sorteaba. Tomó ~12 segundos. Mismos resultados.

### Fase 5: Documentar
Capturamos evidencia visual en cada paso y documentamos los resultados para poder compararlos.

---

## Problemas Encontrados y Cómo los Resolvimos

### Problema 1: PowerShell no ejecutaba heredoc bash
**Lo que pasó:** Intentamos usar `<< 'EOF'` en una sola línea de PowerShell. PowerShell interpretó TODO el código Python como comandos PowerShell, lo que obviamente no funcionó.

**Solución:** Creamos el archivo Python localmente en PowerShell usando `@" "@ | Out-File`, luego lo copiamos al contenedor con `docker compose cp`.

**Aprendizaje:** Evitar escribir scripts multi-línea directamente en PowerShell. Los string literals heredoc de PowerShell y bash tienen sintaxis completamente diferente.

### Problema 2: Dockerfile no tenía Python
**Lo que pasó:** El Dockerfile original para Spark no incluía Python 3, así que cuando intentamos ejecutar PySpark falló.

**Solución:** Agregamos `python3` y `python3-pip` al Dockerfile, más un symlink `python → python3` para compatibilidad.

**Aprendizaje:** PySpark necesita Python en el contenedor. Los Dockerfiles de Spark estándar no incluyen Python por defecto.

### Problema 3: HDFS path no existía después de `docker compose down -v`
**Lo que pasó:** Ejecutamos `docker compose down -v` (el `-v` borra volúmenes). Cuando levantamos el cluster de nuevo, HDFS estaba vacío y Spark no podía leer los datos.

**Solución:** Recargamos los datos con `hdfs dfs -mkdir -p` y `hdfs dfs -put` nuevamente.

**Aprendizaje:** El flag `-v` en `docker compose down` es destructivo. Después, necesitas recargar datos. En producción, los volúmenes estarían separados para no perder datos.

### Problema 4: Output de Spark ya existía
**Lo que pasó:** Ejecutamos Spark dos veces. La segunda vez, Spark intentó escribir a `/user/root/wordcount/output-spark` pero ya existía.

**Solución:** Limpiar con `hdfs dfs -rm -r /user/root/wordcount/output-spark` antes de ejecutar Spark nuevamente.

**Aprendizaje:** Spark no sobrescribe directorios de salida. Necesitas borrar explícitamente o usar un nombre diferente cada vez.

---

## Resultados Finales

| Métrica | MapReduce | Spark |
|---------|-----------|-------|
| Tiempo | ~43s | ~12s |
| Mappers | 4 | (automático) |
| Palabras únicas | 182 | 182 |
| Bytes procesados | 1,980 | 1,980 |
| Código | JAR compilado | 14 líneas Python |

**Conclusión:** Spark fue 3.6x más rápido en este caso. Para datasets pequeños, la diferencia es menos dramática que con datos grandes, pero el código PySpark fue más fácil de leer y modificar.

---

## Archivos Generados

- `wordcount.py` — Script PySpark usado
- `Dockerfile.spark-ubuntu` — Dockerfile personalizado con Python
- `docker-compose.yml` — Configuración del cluster
- Outputs en HDFS:
  - `/user/root/wordcount/output-mr/part-r-00000`
  - `/user/root/wordcount/output-spark/part-00000`

---

## Cómo Reproducir

1. Levanta el cluster: `docker compose up -d`
2. Carga datos: `docker compose exec namenode bash -c "hdfs dfs -mkdir -p /user/root/wordcount/input && hdfs dfs -put /workspace/data/wordcount/*.txt /user/root/wordcount/input/"`
3. Ejecuta MapReduce: `docker compose exec namenode bash -c "hadoop jar /opt/hadoop-3.2.1/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.2.1.jar wordcount /user/root/wordcount/input /user/root/wordcount/output-mr"`
4. Ejecuta Spark: `docker compose exec spark-master spark-submit --master spark://spark-master:7077 --conf spark.hadoop.fs.defaultFS=hdfs://namenode:9000 wordcount.py`
5. Revisa outputs: `docker compose exec namenode bash -c "hdfs dfs -cat /user/root/wordcount/output-mr/part-r-00000"`

---

**Estado:**  Taller completado con éxito