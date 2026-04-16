# Brief: Taller 5 — Open Table Formats con Apache Iceberg

## El problema que resuelve este taller

### Parquet plano tiene limitaciones fundamentales

En el **Taller 4** aprendimos que Parquet es un formato columnar eficiente para cargas analíticas. Sin embargo, en el momento en que un sistema de datos necesita comportarse como una fuente de verdad operacional, Parquet plano se queda corto:

**1. Sin ACID**
Un archivo Parquet es inmutable. No existe un mecanismo nativo para hacer `UPDATE` de una fila o `DELETE` de un subconjunto de registros. La unica opcion es leer todo el archivo, aplicar la transformacion en memoria y reescribir todo — lo cual es costoso en tiempo y computo para datasets grandes, y no ofrece ninguna garantia de atomicidad: si el proceso falla a mitad, los datos quedan en estado inconsistente.

**2. Sin historial de cambios (no hay time travel)**
Una vez que reescribes un archivo Parquet, el estado anterior desaparece. Si un analista hace un `DELETE` masivo accidental, no hay forma de recuperar los datos sin un backup externo. En produccion, esto es un riesgo operacional serio.

**3. Schema evolution requiere coordinacion externa**
Si agregas una columna a los archivos nuevos y tienes archivos viejos sin esa columna en el mismo "dataset", cada lector debe manejar el desajuste de schema por su cuenta. No hay un contrato central que garantice compatibilidad.

---

## La solucion: Apache Iceberg sobre MinIO

**Apache Iceberg** es un open table format que agrega una capa de metadatos sobre archivos Parquet. Esos metadatos (snapshots, manifests, manifest lists) permiten:

- **ACID transaccional**: `UPDATE` y `DELETE` crean un nuevo snapshot que apunta a los archivos modificados. Los archivos sin cambios se reusan sin copiarse.
- **Time Travel**: cada snapshot es un estado completo e inmutable de la tabla. Se puede leer cualquier version anterior con `VERSION AS OF <snapshot_id>`.
- **Schema Evolution nativa**: Iceberg usa IDs internos para las columnas. Agregar una columna no requiere reescribir los archivos existentes — las filas antiguas simplemente muestran `NULL` en la columna nueva.
- **Optimistic Concurrency Control**: multiples escritores pueden operar en paralelo con garantias de aislamiento.

**MinIO** actua como object storage compatible con la API de S3. Esto acerca la arquitectura al mundo real de produccion (AWS S3, GCS, Azure Blob) y permite que el mismo codigo funcione en cloud con un cambio minimo de configuracion.

---

## Lo que se demuestra en este taller

El notebook `taller5.ipynb` guia al estudiante a traves de cuatro demostraciones concretas:

| Seccion | Que se hace | Concepto demostrado |
|---------|------------|---------------------|
| Parte 1 | Escribir y "actualizar" Parquet plano | El problema: reescritura total |
| Parte 2 | Crear tabla Iceberg, explorar archivos en MinIO | Estructura de metadatos de Iceberg |
| Parte 3 | `UPDATE` y `DELETE` con Spark SQL | ACID transaccional |
| Parte 4 | `VERSION AS OF <snapshot_id>` | Time Travel |
| Parte 5 | `ALTER TABLE ... ADD COLUMN` | Schema Evolution sin reescritura |

---

## Conexion con el resto de la serie

Los estudiantes ya trabajaron con Parquet en el Taller 4, por lo que el contraste es inmediato y tangible. El mismo dataset de 50 ventas se usa en ambos talleres para que la comparacion sea directa.

En el **Taller 6** se agregara Trino al stack, completando la arquitectura de un lakehouse moderno donde distintos motores de consulta (Spark, Trino, Flink) pueden leer las mismas tablas Iceberg de forma consistente.
