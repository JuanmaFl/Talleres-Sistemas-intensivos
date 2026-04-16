# Lab 3: WordCount con Spark

## Objetivo

Ejecutar el mismo wordcount que el Lab 2 pero usando Apache Spark. Observar el DAG de ejecucion en Spark UI, comparar el tiempo con MapReduce y verificar que los resultados sean equivalentes.

## Pasos

### 1. Ejecutar el wordcount con Spark

Asegurate de que los datos ya esten en HDFS (si corriste `make hdfs-init` en el Lab 2, ya estan listos).

```bash
make wordcount-spark
```

El script:
1. Limpia cualquier output anterior de Spark en HDFS.
2. Ejecuta `spark-submit` desde el contenedor `spark-master` apuntando al script `/jobs/wordcount.py`.
3. Mide el tiempo de ejecucion.
4. Muestra el tiempo al final.

**Anota el tiempo que aparece al final de la salida.**

Tiempo Spark: _________ segundos

### 2. Abrir Spark UI durante o despues de la ejecucion

Abre `http://localhost:8080`. Si el job todavia esta corriendo, veras la aplicacion `WordCount-Spark` en la tabla **Running Applications**. Si ya termino, estara en **Completed Applications**.

Haz clic en el nombre de la aplicacion para ver los detalles.

### 3. Explorar el DAG en Spark UI

Dentro de los detalles de la aplicacion:

1. Ve a la pestana **Stages**.
2. Haz clic en cada stage para ver el DAG de ese stage.
3. Identifica cuantos stages hay en total.
4. Busca el stage que corresponde al `reduceByKey`: ese es el punto de shuffle.

### 4. Comparar el output con el de MapReduce

El resultado de Spark quedo en `/user/root/wordcount/output-spark`. Para comparar:

```bash
docker compose exec -T namenode bash -c \
  "hdfs dfs -ls /user/root/wordcount/"
```

Veras dos directorios: `output-mr` y `output-spark`. Para ver los primeros registros de Spark:

```bash
docker compose exec -T namenode bash -c \
  "hdfs dfs -cat /user/root/wordcount/output-spark/part-00000 | head -n 20"
```

Nota: el output de Spark tiene multiples archivos `part-00000`, `part-00001`, etc. (uno por particion), mientras que MapReduce produjo un unico `part-r-00000`.

### 5. Leer el script wordcount.py

Abre el archivo `jobs/wordcount.py` y lee cada linea. Identifica:
- Que hace `flatMap`.
- Que hace `map`.
- Que hace `reduceByKey`.
- Que hace `sortBy`.
- Cual es la accion que dispara la ejecucion (`saveAsTextFile`).

## Preguntas de analisis

1. ¿Cuanto tiempo tardo Spark? Compara con el tiempo de MapReduce del Lab 2.

2. ¿Cuantos stages aparecen en el DAG de Spark? ¿Que operacion marca el limite entre stages (el punto de shuffle)?

3. ¿Que diferencia ves entre el DAG de Spark y las fases Map/Shuffle/Reduce de MapReduce? ¿Que ventajas tiene el DAG?

4. El output de MapReduce estaba ordenado alfabeticamente (`part-r-00000` con palabras en orden A-Z). ¿Esta ordenado el output de Spark? ¿Por que?

5. ¿Por que el output de Spark tiene multiples archivos `part-XXXXX` en lugar de uno solo como en MapReduce?

6. ¿Cual es la diferencia entre una **transformacion** y una **accion** en Spark? Da un ejemplo de cada una usando el codigo de `wordcount.py`.

## Evidencia minima

- Captura del DAG de la aplicacion en Spark UI mostrando los stages.
- El tiempo anotado en segundos para comparar con el Lab 2.
