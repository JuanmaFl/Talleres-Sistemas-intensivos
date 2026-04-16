# Taller Spark: De MapReduce a Spark — El mismo problema, dos engines

Este repositorio propone la segunda practica de la serie de sistemas intensivos en datos. Partiendo del cluster Hadoop del Taller 2, extiende el entorno con un modo Spark Standalone y ejecuta el **mismo wordcount** con ambos engines para que los estudiantes entiendan, con numeros concretos, por que Spark desplazo a MapReduce.

## Objetivos de aprendizaje

- Extender un cluster Hadoop existente agregando Spark Standalone.
- Ejecutar el mismo job de wordcount con MapReduce y con Spark sobre los mismos datos.
- Comparar tiempos de ejecucion y analizar las diferencias.
- Leer el DAG de una aplicacion Spark en Spark UI e identificar stages y tasks.
- Explicar por que Spark es mas eficiente que MapReduce para datos en memoria (DAG, in-memory shuffle, lazy evaluation).
- Contrastar la complejidad del codigo: WordCount en Java MapReduce vs PySpark.
- Anticipar lo que DataFrames y Parquet (Taller 4) agregan sobre esta base.

## Estructura del repositorio

```text
.
├── config/
│   └── hadoop.env          # Configuracion de Hadoop (identica al Taller 2)
├── data/
│   └── wordcount/
│       ├── introduccion.txt
│       ├── hdfs.txt
│       ├── mapreduce.txt
│       └── spark.txt       # Nuevo en este taller
├── docs/
│   ├── brief.md            # Resumen y contexto pedagogico
│   ├── architecture.md     # Arquitectura del cluster y comparacion de engines
│   └── instructor-guide.md # Guia del docente con agenda de 2.5 horas
├── jobs/
│   └── wordcount.py        # Job PySpark de wordcount
├── labs/
│   ├── lab-01-cluster-setup.md
│   ├── lab-02-wordcount-mr.md
│   ├── lab-03-wordcount-spark.md
│   └── lab-04-comparacion.md
├── scripts/
│   ├── common.sh           # Funciones compartidas (HDFS + YARN + Spark)
│   ├── bootstrap-hdfs.sh   # Carga los datos en HDFS
│   ├── run-wordcount-mr.sh # Ejecuta wordcount con MapReduce
│   ├── run-wordcount-spark.sh # Ejecuta wordcount con Spark
│   ├── compare.sh          # Ejecuta ambos y muestra tabla de tiempos
│   └── status.sh           # Muestra estado del cluster e interfaces
├── docker-compose.yml
├── Makefile
└── README.md
```

## Requisitos

- Docker Desktop o Docker Engine con `docker compose`
- **10 GB de RAM disponibles** para contenedores (mas que el Taller 2 porque agrega Spark Master + 2 Workers)
- 15 GB de espacio libre en disco
- En Apple Silicon, habilitar emulacion `amd64` en Docker Desktop

## Inicio rapido

```bash
make up          # Levanta 10 contenedores (7 Hadoop + 3 Spark)
make hdfs-init   # Carga los archivos de texto en HDFS
make compare     # Ejecuta wordcount con ambos engines y compara tiempos
```

## Interfaces web

| Interfaz | URL | Descripcion |
|----------|-----|-------------|
| NameNode UI | http://localhost:9870 | Estado de HDFS y DataNodes |
| ResourceManager UI | http://localhost:8088 | Jobs YARN (MapReduce) |
| JobHistory Server | http://localhost:19888 | Historial de jobs MapReduce |
| Spark Master UI | http://localhost:8080 | Workers Spark y aplicaciones |

## Flujo del taller

1. Levantar el cluster extendido y verificar las 4 interfaces web (Lab 1).
2. Cargar los datos en HDFS con `make hdfs-init`.
3. Ejecutar wordcount con MapReduce, anotar el tiempo, analizar en YARN UI (Lab 2).
4. Ejecutar wordcount con Spark, anotar el tiempo, analizar el DAG en Spark UI (Lab 3).
5. Ejecutar `make compare` y analizar la tabla de tiempos y diferencias de codigo (Lab 4).

## Comandos disponibles

```bash
make up              # Levanta el cluster completo
make down            # Apaga el cluster (preserva datos)
make clean           # Apaga y elimina todos los volumenes
make ps              # Lista los 10 servicios y su estado
make logs            # Logs en vivo de namenode, resourcemanager y spark-master
make hdfs-init       # Prepara directorios y carga datos en HDFS
make wordcount-mr    # Ejecuta wordcount con MapReduce y mide el tiempo
make wordcount-spark # Ejecuta wordcount con Spark y mide el tiempo
make compare         # Ejecuta ambos y muestra tabla de tiempos comparativa
make status          # Muestra estado general e interfaces disponibles
```

## Material docente incluido

- [Resumen del taller](docs/brief.md)
- [Arquitectura del laboratorio](docs/architecture.md)
- [Guia del docente](docs/instructor-guide.md)
- [Lab 1: Levantar el cluster](labs/lab-01-cluster-setup.md)
- [Lab 2: WordCount con MapReduce](labs/lab-02-wordcount-mr.md)
- [Lab 3: WordCount con Spark](labs/lab-03-wordcount-spark.md)
- [Lab 4: Comparacion y analisis](labs/lab-04-comparacion.md)

## Hilo conductor de la serie

| Taller | Storage | Engine | Formato | Concepto central |
|--------|---------|--------|---------|-----------------|
| Taller 2 | HDFS | MapReduce | Texto plano | Procesamiento batch distribuido |
| **Taller 3** | **HDFS** | **MapReduce + Spark** | **Texto plano** | **Por que Spark reemplaza a MapReduce** |
| Taller 4 | HDFS | Spark | Parquet | DataFrames y formatos columnares |

## Relacion con las diapositivas del curso

Este taller aterriza las siguientes ideas de la presentacion del curso:

- **De batch a in-memory**: por que mantener datos en RAM cambia el orden de magnitud del rendimiento.
- **DAG vs etapas discretas**: como Spark optimiza el plan de ejecucion antes de correr cualquier tarea.
- **Lazy evaluation**: acumulacion de transformaciones y ejecucion diferida.
- **Ecosistema Spark**: relacion entre Spark Core (RDDs), Spark SQL (DataFrames) y el scheduler del cluster.

## Nota sobre los tiempos esperados

Con el dataset incluido (4 archivos de texto, ~3 KB en total), la diferencia de tiempo puede ser modesta porque el overhead de arranque de Spark es comparable al tiempo de computo. Esto es parte de la leccion: la ventaja de Spark se amplifica con datasets mas grandes y con algoritmos iterativos. Ver `docs/instructor-guide.md` para mas detalles.

## Siguientes extensiones

El Taller 4 usa el mismo HDFS pero introduce:
- DataFrames de Spark SQL en lugar de RDDs.
- Formato Parquet en lugar de archivos de texto.
- El optimizador de consultas Catalyst de Spark.

Eso representa el siguiente salto de abstraccion: de `reduceByKey` a `GROUP BY` en SQL distribuido.
