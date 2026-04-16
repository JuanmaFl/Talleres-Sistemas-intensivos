# Lab 2: WordCount con MapReduce

## Objetivo

Repetir el wordcount del Taller 2 en el nuevo entorno para establecer una linea base de tiempo. Este resultado sera el punto de comparacion para el Lab 3 (Spark).

## Pasos

### 1. Cargar los datos en HDFS

```bash
make hdfs-init
```

Este comando espera a que HDFS este disponible, crea la estructura de directorios y copia los 4 archivos de texto al directorio de entrada en HDFS (`/user/root/wordcount/input`).

Para verificar que los archivos se cargaron correctamente, puedes abrir NameNode UI (`http://localhost:9870`) y navegar a **Utilities → Browse the file system** hacia la ruta `/user/root/wordcount/input`.

### 2. Ejecutar el wordcount con MapReduce

```bash
make wordcount-mr
```

El script:
1. Limpia cualquier output anterior de MapReduce.
2. Busca el jar `hadoop-mapreduce-examples-*.jar` dentro del contenedor namenode.
3. Ejecuta `hadoop jar <jar> wordcount <input> <output-mr>`.
4. Mide el tiempo de ejecucion.
5. Muestra las primeras 30 lineas del resultado.

**Anota el tiempo que aparece al final de la salida.**

Tiempo MapReduce: _________ segundos

### 3. Observar el job en YARN UI

Mientras el job esta corriendo (o inmediatamente despues), abre `http://localhost:8088`.

- Ve a **Applications → FINISHED** si el job ya termino.
- Haz clic en el nombre del job para ver los detalles.
- Busca la columna **Maps** y **Reduces** en la tabla de counters.

### 4. Ver el historial en JobHistory Server

Abre `http://localhost:19888` y busca el job recien completado. Navega a:
- **Map Tasks**: cuantos mappers se usaron y cuanto tardaron.
- **Reduce Tasks**: cuantos reducers se usaron.
- **Counters**: busca `HDFS_BYTES_READ` y `HDFS_BYTES_WRITTEN`.

### 5. Verificar el output en HDFS

El resultado quedo en `/user/root/wordcount/output-mr`. Puedes verlo en NameNode UI o ejecutar:

```bash
docker compose exec -T namenode bash -c \
  "hdfs dfs -cat /user/root/wordcount/output-mr/part-r-00000 | head -n 20"
```

## Preguntas de analisis

1. ¿Cuanto tiempo tardo el job completo? Anota el tiempo reportado por el script.

2. ¿Cuantos mappers y cuantos reducers se usaron? ¿Que determino ese numero?

3. ¿Que ocurre en la fase de shuffle? Describe en tus propias palabras el flujo de datos entre la salida del mapper y la entrada del reducer.

4. En los contadores del job, busca `FILE_BYTES_WRITTEN`. ¿Que representa ese numero? ¿Por que es mayor que el tamano de los archivos de entrada?

5. ¿El resultado esta ordenado por frecuencia o por orden alfabetico? ¿Por que?

## Evidencia minima

- Captura del job completado en YARN UI o JobHistory Server con el tiempo total visible.
- El tiempo anotado en segundos para comparar con el Lab 3.
