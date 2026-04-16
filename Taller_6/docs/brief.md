# Brief: Taller 6 — Arquitectura Lakehouse

## Problema que resuelve este taller

En un entorno de produccion real, los sistemas de datos enfrentan tres desafios que los talleres anteriores no abordaron completamente:

1. **Los datos llegan en lotes sucesivos.** No es posible reescribir la tabla completa cada vez que llega un nuevo archivo. Se necesita un mecanismo de `append` que preserve el historial y permita auditar que lote fue ingestado y cuando.

2. **Los pipelines deben ser idempotentes.** Si el job de transformacion falla a mitad y se re-ejecuta, el resultado debe ser el mismo. Sobrescribir la tabla con `createOrReplace` garantiza idempotencia para las capas Silver y Gold.

3. **Multiples equipos con herramientas distintas necesitan acceder a los mismos datos.** Los ingenieros de datos usan Spark. Los analistas prefieren SQL puro con Trino o herramientas de BI. Sin un catalogo compartido, cada equipo tendria su propia copia de los datos, generando inconsistencias.

## Solucion: arquitectura Lakehouse

El Lakehouse combina la escalabilidad del Data Lake (almacenamiento barato en S3/MinIO) con las garantias del Data Warehouse (transacciones ACID, versionado, esquema aplicado).

La arquitectura de **tres capas** (Bronze → Silver → Gold) es la implementacion practica mas usada en la industria:

- **Bronze** recibe los datos crudos tal como llegan, sin transformacion. Sirve como fuente de verdad auditada.
- **Silver** limpia, valida y enriquece. Es la capa de trabajo para los ingenieros.
- **Gold** agrega metricas de negocio. Es lo que ven los dashboards y los analistas.

El componente clave que hace posible el acceso multimotor es el **catalogo REST de Iceberg**: tanto Spark como Trino lo consultan para encontrar las tablas, sus esquemas y la ubicacion de los archivos en MinIO. El resultado es que un analista puede ejecutar SQL en Trino y obtener exactamente la misma tabla que un ingeniero ve en Spark SQL.

## Conexion con los talleres anteriores

Este taller no introduce conceptos radicalmente nuevos — los integra:

| Concepto               | Introducido en | Usado en T6 |
|------------------------|----------------|-------------|
| Procesamiento paralelo | T2 (MapReduce) | Spark workers |
| Spark API              | T3             | Jobs Bronze/Silver/Gold |
| Parquet / columnar     | T4             | Formato de almacenamiento Iceberg |
| MinIO como S3          | T5             | Bucket `warehouse` |
| Iceberg snapshots      | T5             | Versionado de Bronze |
| Trino                  | **T6 (nuevo)** | Query engine independiente |

El Taller 6 es el cierre natural del ciclo: demuestra que todos los componentes trabajando juntos forman un sistema de datos real, no solo una coleccion de herramientas aisladas.
