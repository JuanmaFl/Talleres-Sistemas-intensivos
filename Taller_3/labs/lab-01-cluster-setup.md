# Lab 1: Levantar el cluster extendido (HDFS + Spark)

## Objetivo

Levantar el cluster combinado de Hadoop y Spark Standalone, verificar que todos los servicios esten activos y familiarizarse con las cuatro interfaces web del taller.

## Pasos

### 1. Levantar todos los servicios

Desde el directorio raiz del repositorio:

```bash
make up
```

Docker Compose iniciara 10 contenedores en total:
- 7 de Hadoop: namenode, datanode1, datanode2, resourcemanager, nodemanager1, nodemanager2, historyserver.
- 3 de Spark: spark-master, spark-worker-1, spark-worker-2.

### 2. Verificar que todos los servicios esten corriendo

```bash
make ps
```

Espera ver 10 filas, todas con estado `running`. Si algun contenedor muestra `exiting` o `restarting`, espera 30 segundos y vuelve a ejecutar `make ps`.

### 3. Abrir las interfaces web

Abre los cuatro enlaces en el navegador:

| Interfaz | URL | Descripcion |
|----------|-----|-------------|
| NameNode UI | http://localhost:9870 | Estado de HDFS, bloques y DataNodes |
| ResourceManager UI | http://localhost:8088 | Jobs YARN activos y completados |
| JobHistory Server | http://localhost:19888 | Historial de jobs MapReduce |
| Spark Master UI | http://localhost:8080 | Workers Spark, aplicaciones activas |

### 4. Verificar los DataNodes en HDFS

En NameNode UI, ir a la seccion **Datanodes**. Deben aparecer 2 DataNodes en estado `In Service`.

### 5. Verificar los workers en Spark UI

En Spark Master UI (`http://localhost:8080`), verificar que aparezcan 2 workers en estado `ALIVE`. Anotar:
- Memoria disponible por worker: ____
- Cores disponibles por worker: ____

### 6. Ver los logs del cluster

```bash
make logs
```

Esto muestra los logs de namenode, resourcemanager y spark-master en tiempo real. Presiona `Ctrl+C` para salir.

## Preguntas de analisis

1. ¿Cuantos contenedores hay en total despues de `make up`? ¿Cuantos son de Hadoop y cuantos de Spark?

2. ¿Que hace el Spark Master? ¿En que se parece y en que se diferencia del YARN ResourceManager?

3. En Spark UI, ¿que informacion muestra sobre los workers que no muestra YARN sobre los NodeManagers?

4. ¿Por que el NameNode tiene acceso a los datos en `/workspace/data` pero los Spark workers tambien tienen ese mismo mount? ¿Que implicacion tiene eso para la ejecucion de jobs?

5. Compara el docker-compose de este taller con el del Taller 2. ¿Que servicios se agregaron? ¿Que cambio en el servicio `namenode`?

## Evidencia minima

- Captura de pantalla de `make ps` mostrando los 10 servicios con estado `running`.
- Captura de pantalla de Spark UI (`http://localhost:8080`) con los 2 workers en estado `ALIVE`.
