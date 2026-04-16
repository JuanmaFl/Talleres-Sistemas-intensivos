# Taller Hadoop: Primer Cluster y WordCount en Batch

Este repositorio propone un taller práctico para estudiantes de sistemas intensivos en datos. La experiencia está alineada con los temas de las diapositivas en `Documentation`, especialmente sistemas de archivos distribuidos, procesamiento batch, ecosistema Hadoop y contraste batch vs streaming.

## Objetivos de aprendizaje

- Entender el rol de HDFS y YARN dentro de un cluster Hadoop.
- Levantar un cluster mínimo local usando Docker Compose.
- Cargar archivos al sistema distribuido de archivos HDFS.
- Ejecutar un job batch de `wordcount` en el cluster.
- Interpretar la salida de un job MapReduce y relacionarla con los conceptos vistos en clase.

## Estructura del repositorio

```text
.
├── config/
├── data/
├── docs/
├── labs/
├── scripts/
├── Documentation/
├── docker-compose.yml
├── Makefile
└── README.md
```

## Requisitos

- Docker Desktop o Docker Engine con `docker compose`
- 8 GB de RAM disponibles para contenedores
- 10 GB de espacio libre
- En Apple Silicon, habilitar emulación `amd64` en Docker Desktop si es necesario

## Inicio rápido

```bash
make up
make hdfs-init
make wordcount
```

Interfaces principales:

- NameNode UI: `http://localhost:9870`
- ResourceManager UI: `http://localhost:8088`
- JobHistory UI: `http://localhost:19888`

## Flujo del taller

1. Levantar el cluster y validar que HDFS y YARN estén activos.
2. Explorar la arquitectura del cluster desde las interfaces web.
3. Crear directorios en HDFS y cargar archivos de ejemplo.
4. Ejecutar `wordcount` como primer proceso batch distribuido.
5. Revisar logs, salida y contadores del job.
6. Discutir cómo cambiaría el enfoque si el caso requiriera streaming.

## Comandos útiles

```bash
make up           # Levanta el cluster
make down         # Apaga el cluster
make clean        # Apaga y elimina volumenes
make ps           # Lista servicios
make logs         # Logs de NameNode y ResourceManager
make hdfs-init    # Prepara directorios y datos en HDFS
make wordcount    # Ejecuta el ejercicio principal
make status       # Muestra endpoints y estado general
```

## Material docente incluido

- [Resumen del taller](docs/brief.md)
- [Arquitectura del laboratorio](docs/architecture.md)
- [Guia del docente](docs/instructor-guide.md)
- [Laboratorio 1: levantar el cluster](labs/lab-01-cluster-setup.md)
- [Laboratorio 2: explorar HDFS](labs/lab-02-hdfs.md)
- [Laboratorio 3: ejecutar WordCount](labs/lab-03-wordcount.md)
- [Retos opcionales](labs/lab-04-retos.md)

## Relacion con las diapositivas

El repositorio aterriza cuatro ideas centrales de la presentación `Introduccion-a-los-Sistemas-Intensivos-en-Datos.pptx`:

- Sistemas de archivos distribuidos: HDFS como capa de almacenamiento.
- Procesamiento distribuido: MapReduce sobre YARN.
- Procesamiento batch: `wordcount` como caso base.
- Ecosistema Hadoop: coordinación entre NameNode, DataNode, ResourceManager y NodeManager.

## Solucion del laboratorio

El repositorio usa el `hadoop-mapreduce-examples` incluido en la imagen para evitar una fase adicional de compilación Java. Esto reduce fricción en la primera práctica y deja una ruta clara para un segundo taller donde los estudiantes implementen su propio job.

## Siguientes extensiones recomendadas

- Repetir el ejercicio con un dataset más grande.
- Cambiar el factor de replicación y observar el impacto.
- Agregar un cuarto nodo de datos.
- Implementar un job MapReduce propio en Java.
- Comparar tiempos contra una versión en Spark.
