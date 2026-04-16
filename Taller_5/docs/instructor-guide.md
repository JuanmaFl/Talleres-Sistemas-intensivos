# Guia del Docente — Taller 5: Open Table Formats con Apache Iceberg

## Objetivo central

Que los estudiantes entiendan, de forma concreta y visual, **que problema resuelve Iceberg que Parquet plano no puede resolver**. Al finalizar, deben poder explicar con sus palabras por que un data lakehouse moderno no puede construirse solo sobre archivos Parquet sin una capa de metadatos transaccional.

---

## Agenda sugerida (2.5 horas)

### Bloque 1: Repaso y contexto (15 min)

**Tema:** Repaso del Taller 4 + presentacion del problema

- Abrir el `brief.md` o la primera celda del notebook para contextualizar
- Preguntar a los estudiantes: "En el Taller 4, si querian corregir el precio de todos los registros de Laptop, que tenian que hacer con Parquet?"
- Esperar respuestas y guiar hacia: "Leer todo, transformar en memoria, reescribir todo"
- Presentar la tabla comparativa del notebook (Parquet vs Iceberg)
- **Enfatizar**: Iceberg no reemplaza Parquet. Iceberg **usa** Parquet para los datos y agrega metadatos por encima

### Bloque 2: Levantar el cluster y explorar MinIO (20 min)

**Tema:** Entender el entorno antes de tocar el notebook

- Ejecutar `make up` desde el directorio del taller
- Explicar los cuatro servicios mientras se levantan: MinIO, mc (configurador), REST catalog, spark-iceberg
- Abrir la **MinIO Console en http://localhost:9001** (admin/password123)
- Mostrar los buckets `warehouse` y `data` — ambos vacios por ahora
- Abrir **Jupyter en http://localhost:8888**
- Ejecutar la celda de la SparkSession y mostrar que no hay errores

**Tip critico para el docente:** La consola de MinIO es la herramienta pedagogica mas poderosa de este taller. Cada vez que se ejecuta una operacion en el notebook, volver a MinIO y mostrar los archivos nuevos que aparecen. Esto hace que la abstraccion de "snapshots" sea concreta y visible.

### Bloque 3: El problema con Parquet plano (20 min)

**Tema:** Lab 2 — demostrar el problema

- Ejecutar las celdas de la Parte 1 del notebook
- Ir a MinIO y mostrar los archivos en `warehouse/ventas_parquet/` — son archivos Parquet planos sin subcarpeta `metadata/`
- Mostrar el codigo del "UPDATE simulado" y enfatizar: esto leyó los 50 registros, transformo en memoria y reescribio los 50 registros, solo para cambiar 5

**Pregunta para el grupo:** "Si este dataset tuviera 500 millones de filas y quisieras actualizar 10 de ellas, cuanto tiempo y costo tendria esta operacion?"

### Bloque 4: Crear tabla Iceberg (20 min)

**Tema:** Lab 2 (continuacion) — crear la tabla y explorar la estructura

- Ejecutar las celdas de la Parte 2
- **Inmediatamente despues**, ir a MinIO Console y mostrar:
  - `warehouse/taller5/ventas/data/` — ver el archivo `.parquet`
  - `warehouse/taller5/ventas/metadata/` — ver el `table-metadata-xxxx.json` y el manifest
- Abrir el archivo JSON de metadata en MinIO y mostrar la estructura (schema, snapshot, location)
- **Concepto clave**: Iceberg sabe exactamente que archivos forman la tabla gracias a los manifests. Con Parquet plano, Spark tenia que listar el directorio entero

### Bloque 5: ACID — UPDATE y DELETE (25 min)

**Tema:** Lab 3 — ver los snapshots crearse

- Ejecutar el UPDATE de la celda 8
- Ir a MinIO — mostrar que aparecio un **nuevo archivo Parquet** en `/data/` y nuevos archivos en `/metadata/`
- El archivo Parquet original **sigue ahi** — no se borro
- Ejecutar el DELETE de la celda 9
- Ir a MinIO de nuevo — aparece otro snapshot y posiblemente archivos de delete

**Concepto clave a enfatizar:** "El DELETE no borra el archivo Parquet original. Crea un archivo de tipo 'delete file' que dice 'ignora estas posiciones'. El archivo fisico solo se borra cuando ejecutas EXPIRE SNAPSHOTS. Esta es la razon por la que el time travel funciona."

- Mostrar la tabla `.history` con los tres snapshots acumulados

### Bloque 6: Time Travel (20 min)

**Tema:** Lab 4 — recuperar el estado anterior

- Ejecutar las celdas de la Parte 4
- Mostrar que el `snapshot_id` inicial devuelve los precios originales de Laptop (1,500,000) en vez del precio actualizado (1,300,000)
- **Escenario practico**: "Imaginen que un analista ejecuto accidentalmente `DELETE FROM ventas` sin WHERE. Sin Iceberg, ¿como recuperan los datos?"
  - Sin Iceberg: esperar a que el equipo de operaciones restaure un backup (horas o dias)
  - Con Iceberg: `INSERT INTO ventas SELECT * FROM ventas VERSION AS OF <last_good_snapshot>` (segundos)

**Reto para adelantados:** mostrar como hacer ROLLBACK con `CALL demo.system.rollback_to_snapshot('taller5.ventas', <snapshot_id>)`

### Bloque 7: Schema Evolution (15 min)

**Tema:** Lab 4 — agregar columna sin romper nada

- Ejecutar las celdas de la Parte 5
- Mostrar que las filas antiguas muestran `NULL` en la columna `descuento` — sin reescritura
- Insertar las dos filas nuevas con `descuento` poblado y mostrar el mix

**Concepto clave:** "Iceberg usa IDs internos para las columnas, no nombres. Si renombras la columna 'precio_unitario' a 'unit_price', Iceberg sabe que es la misma columna (mismo ID) y no pierde los datos."

### Bloque 8: Discusion y cierre (15 min)

**Preguntas de cierre sugeridas:**

1. "¿En que escenario de negocios real es indispensable el time travel?" (Auditorias regulatorias, compliance GDPR, debugging de pipelines de ML)
2. "¿Que pasa con el espacio en disco si nunca ejecutas EXPIRE SNAPSHOTS?" (Crece indefinidamente — en produccion hay politicas de retencion)
3. "¿Por que usamos MinIO en vez de HDFS en este taller?" (Preparar para S3 en cloud, es el estandar en lakehouses modernos)
4. "En el Taller 6, Trino va a leer estas mismas tablas Iceberg. ¿Que necesita saber Trino para leer la tabla?" (La ubicacion del catalogo REST y las credenciales de MinIO — el formato Iceberg es el contrato)

---

## Conceptos a enfatizar

### Snapshot isolation

Cada operacion de escritura (INSERT, UPDATE, DELETE) crea un **snapshot atomico**. Los lectores que empezaron antes de la escritura siguen viendo el snapshot anterior — nunca ven datos parcialmente escritos. Esto es lo que significa "aislamiento de snapshots".

### Metadata files

La jerarquia de metadatos (table metadata → manifest list → manifest files → data files) permite a Iceberg:
- Encontrar rapidamente que archivos son relevantes para una query (partition pruning)
- Hacer comprobaciones de atomicidad al confirmar una escritura
- Mantener el historial de snapshots para time travel

### Manifest lists y manifest files

Una manifest list es una lista de manifests activos para un snapshot. Cada manifest file contiene la lista de archivos de datos con sus estadisticas. Esta doble indirection permite que un UPDATE que modifica 1% de los datos solo reescriba 1% de los manifests — el resto se reutiliza.

---

## Errores comunes y como manejarlos

| Problema | Causa probable | Solucion |
|----------|---------------|---------|
| `Connection refused` al crear SparkSession | El servicio `rest` no termino de iniciar | Esperar 30s mas y reintentar |
| `NoSuchTableException` | Se ejecuto la celda de CREATE sin ejecutar la de DROP primero | Ejecutar la celda 6 desde el principio (tiene el DROP IF EXISTS) |
| Jupyter no abre | El contenedor `spark-iceberg` no levanto correctamente | `make logs` para ver el error |
| MinIO console muestra buckets vacios | El servicio `mc` fallo al crear los buckets | `docker compose restart mc` |
| El UPDATE no crea nuevos archivos en MinIO | El modo Copy-on-Write puede agrupar cambios | Refrescar la consola de MinIO |

---

## Evidencias sugeridas

Para la evaluacion del taller, se recomienda pedir alguna de las siguientes evidencias:

1. **Captura de pantalla de MinIO Console** mostrando la carpeta `metadata/` con los archivos JSON y Avro despues de hacer el UPDATE
2. **Output del historial** (`demo.taller5.ventas.history`) con al menos 3 snapshots y sus operaciones
3. **Comparacion de precios** de Laptop entre el snapshot inicial y el snapshot actual (time travel)
4. **Schema DESCRIBE** de la tabla antes y despues de agregar la columna `descuento`
5. **Respuesta escrita** a las preguntas de analisis de la celda final del notebook

---

## Material de referencia

- Documentacion oficial Iceberg: https://iceberg.apache.org/docs/latest/
- Spark + Iceberg quickstart: https://iceberg.apache.org/docs/latest/spark-getting-started/
- MinIO + Iceberg: https://min.io/docs/minio/linux/integrations/using-minio-with-apache-iceberg.html
- Catalogo REST Iceberg: https://iceberg.apache.org/docs/latest/rest-catalog/
