# Laboratorio 2: Explorar HDFS

## Objetivo

Crear la estructura de trabajo en HDFS y cargar los archivos que se usaran en el job batch.

## Pasos

1. Inicializa HDFS con el dataset del taller:

   ```bash
   make hdfs-init
   ```

2. Lista los archivos de entrada:

   ```bash
   docker compose exec -T namenode hdfs dfs -ls /user/root/wordcount/input
   ```

3. Visualiza uno de los archivos:

   ```bash
   docker compose exec -T namenode hdfs dfs -cat /user/root/wordcount/input/introduccion.txt
   ```

4. Revisa el bloque y la replicacion desde la UI de HDFS.

## Preguntas de analisis

- ¿En que se diferencia `hdfs dfs -ls` de `ls` local?
- ¿Que ventaja tiene guardar estos archivos en HDFS y no solo en el disco del host?
- ¿Que significa que la replicacion este en `2`?

## Evidencia minima

- Salida de `hdfs dfs -ls`
- Captura del directorio en la UI del NameNode
