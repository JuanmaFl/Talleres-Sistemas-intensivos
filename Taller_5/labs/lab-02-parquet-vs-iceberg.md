# Lab 2: El problema con Parquet plano vs. Iceberg

## Objetivo

Entender concretamente que limitaciones tiene Parquet como formato de almacenamiento cuando se necesita modificar datos, y comparar el resultado con una tabla Iceberg.

---

## Tiempo estimado

25 minutos

---

## Prerequisitos

- Lab 1 completado (cluster corriendo, Jupyter abierto)
- SparkSession ejecutada correctamente

---

## Parte A: Escribir y "actualizar" datos en Parquet plano

### Paso 1: Cargar el CSV y escribir como Parquet

Ejecutar la **celda 4** del notebook (Parte 1).

Esta celda:
1. Lee el archivo `ventas.csv` con 50 registros
2. Calcula la columna `total`
3. Escribe los datos como Parquet plano en `s3://warehouse/ventas_parquet/`

### Paso 2: Explorar en MinIO

Ir a la MinIO Console → bucket `warehouse` → carpeta `ventas_parquet/`.

Observar:
- Hay uno o varios archivos `.parquet`
- **No hay subcarpeta `metadata/`** — esto es Parquet plano, sin gestion de versiones

### Paso 3: Intentar actualizar un registro

Ejecutar la **celda 4b** del notebook (la simulacion de UPDATE en Parquet plano).

Leer el codigo con atencion: para cambiar el precio de los registros de Laptop, el proceso tuvo que:
1. Leer los **50 registros** completos
2. Aplicar la transformacion en memoria
3. Reescribir los **50 registros** en el archivo

Ir a MinIO — los archivos en `ventas_parquet/` fueron reemplazados. No hay rastro del estado anterior.

> **Reflexion:** En un dataset real de 500 millones de filas que pesa 2 TB en disco, este proceso tomaria horas y tendria un costo computacional enorme — solo para actualizar un puñado de registros.

---

## Parte B: Crear la tabla Iceberg y comparar

### Paso 4: Crear la tabla Iceberg

Ejecutar la **celda 6** del notebook (Parte 2).

Esta celda:
1. Crea el namespace `demo.taller5`
2. Escribe los datos como tabla Iceberg en el catalogo REST
3. Muestra los primeros 5 registros para verificar

### Paso 5: Explorar la estructura en MinIO

Ir a MinIO Console → bucket `warehouse`.

Ahora debes ver una nueva ruta: `warehouse/taller5/ventas/`

Explorar las dos subcarpetas:

**Carpeta `data/`:**
- Contiene uno o varios archivos `.parquet`
- Son los datos reales — exactamente igual que el Parquet plano

**Carpeta `metadata/`:**
- `v1.metadata.json` — metadata de la tabla: schema, propiedades, puntero al primer snapshot
- `snap-<id>-1.avro` — manifest list del snapshot de creacion
- `<uuid>-m0.avro` — manifest file con la lista de archivos de datos y estadisticas

> **Punto clave:** Los datos fisicos son identicos (Parquet), pero Iceberg agrego una capa de metadatos que registra exactamente que archivos forman el estado actual de la tabla.

### Paso 6: Explorar metadatos desde Spark

Ejecutar la **celda 6b** del notebook.

Esta celda muestra:
- Los archivos de datos registrados en la tabla (con su tamano y numero de registros)
- El snapshot actual con su `snapshot_id` y la operacion (`append`)

---

## Comparativa visual

| Aspecto | Parquet plano (`ventas_parquet/`) | Iceberg (`warehouse/taller5/ventas/`) |
|---------|----------------------------------|--------------------------------------|
| Archivos de datos | `.parquet` en el directorio | `.parquet` en `/data/` |
| Metadatos | Ningunos | `table-metadata.json`, manifest list, manifests en `/metadata/` |
| Historial de cambios | No existe | Cada escritura crea un snapshot |
| Para hacer UPDATE | Reescribir todo | Crear nuevo snapshot (siguiente lab) |
| Para leer estado anterior | Imposible | `VERSION AS OF <snapshot_id>` |

---

## Preguntas de analisis

1. **¿Cuantos archivos creo Iceberg** al crear la tabla? ¿Cuantos son de datos y cuantos son de metadatos?

2. **¿Que contiene el archivo `v1.metadata.json`?** Abrirlo en MinIO (clic en el archivo → preview) y describir los campos principales que puedes identificar.

3. **¿Que hay en el archivo de manifest (`-m0.avro`)?** No podras abrirlo directamente (es formato Avro binario), pero ejecuta la consulta `SELECT * FROM demo.taller5.ventas.files` en el notebook — ¿que informacion muestra?

4. En el Parquet plano, Spark necesita **listar el directorio** para saber que archivos leer. En Iceberg, Spark **consulta el manifest**. ¿Que ventaja da esto en un dataset con miles de archivos?

---

## Evidencia minima

- Captura de pantalla de MinIO mostrando la estructura `warehouse/taller5/ventas/` con las carpetas `data/` y `metadata/`
- Captura del output de `SELECT * FROM demo.taller5.ventas.files` mostrando los archivos registrados
