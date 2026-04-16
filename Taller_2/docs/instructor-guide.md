# Guia del Docente

## Objetivo de la sesion

Llevar a los estudiantes desde la idea abstracta de procesamiento batch distribuido hasta una ejecucion real de `wordcount` en un cluster Hadoop minimo.

## Relacion con las diapositivas

La secuencia del taller aterriza estos temas de `Introduccion-a-los-Sistemas-Intensivos-en-Datos.pptx`:

- Sistemas de archivos distribuidos.
- Procesamiento batch vs streaming.
- Ecosistema Hadoop.
- Rol del ingeniero de datos en pipelines distribuidos.

## Agenda sugerida para 2 horas

1. 15 min: repaso conceptual de HDFS, YARN y batch processing.
2. 20 min: levantar el cluster y recorrer interfaces.
3. 20 min: comandos basicos en HDFS.
4. 25 min: ejecutar `wordcount`.
5. 20 min: interpretar salida, logs y contadores.
6. 20 min: discusion sobre extensiones y comparacion con streaming.

## Conceptos que conviene enfatizar

- El NameNode no almacena los datos completos: administra metadatos.
- Los DataNodes almacenan bloques y permiten replicacion.
- YARN separa gestion de recursos de ejecucion de tareas.
- `wordcount` es batch porque opera sobre un conjunto finito de datos ya acumulados.

## Evidencias sugeridas para entrega

- Captura del NameNode con el directorio de entrada.
- Captura del ResourceManager con el job completado.
- Salida parcial del archivo `part-r-00000`.
- Respuesta corta sobre por que el ejercicio corresponde a batch y no a streaming.

## Preguntas de cierre

- ¿Que pasa si subimos el factor de replicacion?
- ¿Que diferencia hay entre HDFS y una carpeta local?
- ¿Por que YARN necesita NodeManagers separados?
- ¿Como cambiaria este flujo si los datos llegaran continuamente?
