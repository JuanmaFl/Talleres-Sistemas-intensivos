# Taller 5 — Open Table Formats con Apache Iceberg

**Equipo:** Samuel Molina · David Felipe Ríos · Juan Manuel Flórez
**Curso:** Sistemas Intensivos en Datos — Universidad EAFIT
**Fecha:** Abril 2026

---

## Qué se hizo

El objetivo era entender de forma concreta qué problema resuelve Apache Iceberg que Parquet plano no puede resolver. Al finalizar el taller, el equipo fue capaz de explicar por qué un data lakehouse moderno no puede construirse solo sobre archivos Parquet sin una capa de metadatos transaccional.

El taller trabaja sobre el mismo dataset de ventas del Taller 4 (50 registros, productos de electrónica vendidos en cinco ciudades colombianas) para que el contraste entre Parquet plano e Iceberg sea inmediato y tangible.

---

## Infraestructura

El cluster corre sobre una instancia EC2 `t3.large` en AWS (Ubuntu 24.04 LTS) con Docker. Cuatro contenedores:

- **minio** — Object storage compatible con S3, sirve como capa de almacenamiento físico
- **mc** — Configurador de MinIO, crea los buckets `warehouse` y `data` al inicio
- **iceberg-rest** — Catálogo REST de Iceberg, gestiona los metadatos de las tablas
- **spark-iceberg** — Apache Spark 3.5.5 con Iceberg 1.8.1, expone Jupyter en el puerto 8888

### Problemas encontrados y soluciones

**Problema con las imágenes de Docker:** La imagen original `tabulario/spark-iceberg:3.5.1_1.5.2` no estaba disponible en Docker Hub. Se reemplazó por `tabulario/spark-iceberg:latest`, que trae Iceberg 1.8.1. La imagen de `minio/mc` también requirió cambio a `latest`.

**Problema con path-style access en S3:** El SDK de AWS construía URLs con virtual-hosted style (`warehouse.minio`) en lugar de path-style (`minio:9000/warehouse`). Se resolvió recreando el contenedor `iceberg-rest` con la variable de entorno `CATALOG_S3_PATH__STYLE__ACCESS=true` y configurando el mismo parámetro en la SparkSession.

**Problema con el hostname del catálogo REST:** La SparkSession usaba `http://rest:8181` como URI del catálogo, pero el hostname del contenedor era `iceberg-rest`. Se corrigió en la configuración de Spark.

**Problema con virtualización en Windows:** La máquina local no tenía SVM activo en la BIOS, lo que impidió correr Docker Desktop localmente. La solución fue desplegar todo en EC2.

---

## Flujo del taller

```
Parte 1: El problema con Parquet plano — simular UPDATE leyendo y reescribiendo todo
         ↓
Parte 2: Crear tabla Iceberg → explorar estructura data/ y metadata/ en MinIO
         ↓
Parte 3: ACID — UPDATE y DELETE transaccionales → ver nuevos snapshots en MinIO
         ↓
Parte 4: Time Travel → leer snapshot inicial con precios originales
         ↓
Parte 5: Schema Evolution → agregar columna descuento sin reescribir datos
```

---

## Evidencias

### SS1 — Servicios Docker corriendo

Muestra el output de `docker-compose ps` con los cuatro servicios activos: `iceberg-rest` (Up), `mc` (Exit 0, normal), `minio` (Up), y `spark-iceberg` (Up) con todos los puertos mapeados correctamente (8888, 8080, 9000, 9001, 8181).

### SS2 — Jupyter y MinIO accesibles

Muestra la interfaz de Jupyter abierta en el navegador (`http://44.211.80.255:8888`) con la carpeta `mine/` que contiene el notebook `taller5.ipynb`. Confirma que el contenedor `spark-iceberg` está sirviendo correctamente.

### SS3 — MinIO Console con buckets vacíos

Muestra la MinIO Console (`http://44.211.80.255:9001`) con los buckets `data` y `warehouse` creados y vacíos. Esto es el estado inicial antes de ejecutar cualquier celda del notebook.

### SS4 — SparkSession creada y tabla ventas_parquet

Muestra dos cosas: la celda de SparkSession con output `SparkSession creada con catalogo Iceberg REST / Version de Spark: 3.5.5`, y la celda que carga los 50 registros del CSV y los escribe como tabla `demo.taller5.ventas_parquet`. Confirma que la conexión con el catálogo REST y MinIO funciona correctamente.

### SS5 — MinIO: carpetas data/ y metadata/ en ventas_parquet

Muestra la estructura de archivos en MinIO en la ruta `warehouse/taller5/ventas_parquet/`. Se pueden ver las carpetas `data/` (archivos Parquet con los datos) y `metadata/` (archivos JSON y Avro con snapshots y manifests). Esta es la diferencia fundamental respecto a Parquet plano: Iceberg agrega una capa de metadatos por encima de los archivos físicos.

### SS6 — Tabla Iceberg principal creada con 50 registros

Muestra la celda que crea la tabla `demo.taller5.ventas` con los 50 registros del dataset. El output incluye los primeros 5 registros con el schema completo (id, fecha, producto, categoria, cantidad, precio_unitario, region, total) y confirma `Total de registros: 50`.

### SS7 — MinIO: carpetas data/ y metadata/ en ventas

Muestra la estructura de archivos en MinIO en la ruta `warehouse/taller5/ventas/`. Igual que SS5, se ven las carpetas `data/` y `metadata/`, confirmando que Iceberg gestiona los metadatos de la tabla principal de ventas.

### SS8 — Archivos de datos y primer snapshot

Muestra el output de la celda que lista los archivos de datos y snapshots de la tabla. Se ve el archivo Parquet inicial con 50 registros (3359 bytes) y el primer snapshot con `operation: append`. El snapshot contiene metadatos completos: added-data-files, added-records, engine-version (Spark 3.5.5), iceberg-version (1.8.1).

### SS9 — UPDATE transaccional: precios ANTES y DESPUÉS

Muestra el UPDATE de precios de Laptop de valores variados (1,500,000 / 1,450,000 / 1,480,000 / 1,520,000 / 1,490,000) a un precio unificado de 1,300,000. El mensaje `UPDATE ejecutado — nuevo snapshot creado` confirma que Iceberg creó un nuevo snapshot atómico sin tocar el snapshot original.

### SS10 — MinIO: dos archivos Parquet después del UPDATE

Muestra la carpeta `warehouse/taller5/ventas/data/` con dos archivos Parquet. El primero fue creado a las 18:36 (INSERT inicial) y el segundo a las 18:39 (UPDATE). El archivo original **no se borró** — Iceberg lo mantiene para soportar time travel. Ambos tienen el mismo tamaño (3.3 KiB) porque el UPDATE reescribió todos los registros afectados en un nuevo archivo.

### SS11 — Historial de snapshots con DELETE incluido

Muestra la tabla de historial de snapshots con 4 entradas: INSERT inicial (23:36), UPDATE de precios (23:39), y dos operaciones de DELETE (23:40 y 23:41). Cada operación creó un snapshot atómico con su propio `snapshot_id` y `made_current_at`. Todos tienen `is_current_ancestor: true`, lo que significa que forman la cadena de herencia de la tabla.

### SS12 — Time Travel: comparación de snapshots

Muestra la funcionalidad de time travel. El primer snapshot (`8056959376138857506`) devuelve los precios originales de Laptop (1,500,000 / 1,450,000 / 1,480,000 / 1,520,000 / 1,490,000). El snapshot actual muestra todos los Laptops con precio 1,300,000 después del UPDATE. Esto demuestra que es posible recuperar el estado exacto de la tabla en cualquier punto del historial sin necesidad de backups.

### SS13 — Schema Evolution: columna descuento agregada

Muestra el schema ANTES de agregar la columna (7 columnas originales) y el resultado después de `ALTER TABLE ADD COLUMN descuento DOUBLE`. Las filas existentes muestran `NULL` en la columna nueva sin ninguna reescritura de datos. Iceberg usa IDs internos para las columnas en lugar de nombres, lo que permite renombrar o agregar columnas sin afectar los datos históricos.

### SS14 — Mix de filas antiguas y nuevas con descuento

Muestra las dos filas nuevas insertadas con descuento poblado (Laptop con 0.1 y Smartphone con 0.05) junto a filas antiguas que tienen `descuento = NULL`. El total final de registros es 52. Esto confirma que el schema evolution funciona correctamente: una misma tabla puede tener filas con diferentes versiones del schema conviviendo sin problemas.

---

## Conceptos demostrados

**Snapshot isolation:** Cada operación de escritura (INSERT, UPDATE, DELETE) crea un snapshot atómico. Los lectores que empezaron antes de la escritura siguen viendo el snapshot anterior — nunca ven datos parcialmente escritos.

**Metadata hierarchy:** La jerarquía de metadatos (table metadata → manifest list → manifest files → data files) permite a Iceberg encontrar rápidamente qué archivos son relevantes para una query, hacer comprobaciones de atomicidad y mantener el historial de snapshots.

**Copy-on-Write:** El UPDATE no modifica los archivos Parquet existentes — crea nuevos archivos con los datos actualizados y actualiza los manifests para apuntar a ellos. Los archivos originales permanecen hasta que se ejecuta `EXPIRE SNAPSHOTS`.

**Schema Evolution sin reescritura:** Iceberg usa IDs internos para las columnas en lugar de nombres de columna. Agregar una columna nueva solo actualiza los metadatos; las filas existentes devuelven `NULL` para la nueva columna sin tocar los archivos físicos.

---

## Cómo reproducir

```bash
# 1. Conectarse a la instancia EC2
ssh -i "taller5-key.pem" ubuntu@44.211.80.255

# 2. Clonar el repositorio
git clone https://github.com/JuanmaFl/Talleres-Sistemas-intensivos.git
cd Talleres-Sistemas-intensivos/Taller_5

# 3. Levantar los servicios
docker-compose up -d
docker-compose up -d --no-deps mc
docker-compose up -d --no-deps rest spark-iceberg

# 4. Recrear el contenedor REST con path-style access
docker stop iceberg-rest && docker rm iceberg-rest
docker run -d --name iceberg-rest --network taller_5_default \
  -e AWS_ACCESS_KEY_ID=admin \
  -e AWS_SECRET_ACCESS_KEY=password123 \
  -e AWS_REGION=us-east-1 \
  -e CATALOG_WAREHOUSE=s3://warehouse/ \
  -e CATALOG_IO__IMPL=org.apache.iceberg.aws.s3.S3FileIO \
  -e CATALOG_S3_ENDPOINT=http://minio:9000 \
  -e CATALOG_S3_PATH__STYLE__ACCESS=true \
  -e CATALOG_CATALOG__IMPL=org.apache.iceberg.jdbc.JdbcCatalog \
  -e CATALOG_URI="jdbc:sqlite:file:/tmp/iceberg_rest_mode=memory" \
  -e CATALOG_JDBC_USER=user \
  -e CATALOG_JDBC_PASSWORD=password \
  -e REST_PORT=8181 \
  -p 8181:8181 \
  tabulario/iceberg-rest:0.10.0

# 5. Abrir Jupyter en el navegador
# http://<IP_EC2>:8888
# Navegar a mine/ → taller5.ipynb
```

**Nota:** La IP de la instancia EC2 cambia en cada reinicio del Learner's Lab. Verificar la IP actual en la consola de AWS antes de conectarse.

---

## Interfaces disponibles

| Interfaz | URL | Credenciales |
|----------|-----|-------------|
| Jupyter + Spark | http://\<IP\>:8888 | — |
| Spark UI | http://\<IP\>:8080 | — |
| MinIO Console | http://\<IP\>:9001 | admin / password123 |
| Iceberg REST API | http://\<IP\>:8181 | — |
