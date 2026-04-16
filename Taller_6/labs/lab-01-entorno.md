# Lab 1 — Levantar el entorno Lakehouse completo

**Duracion estimada:** 20 minutos
**Objetivo:** Verificar que todos los servicios del entorno Lakehouse estan funcionando
y entender el rol de cada componente.

---

## Paso 1: Iniciar el entorno

Desde el directorio raiz del repositorio:

```bash
make up
```

Espera aproximadamente **90 segundos** para que todos los servicios inicien.
MinIO tarda unos segundos en responder al healthcheck antes de que los demas servicios arranquen.

Verifica el estado:

```bash
make status
```

Deberias ver algo como:

```
NAME            IMAGE                                        STATUS
minio           minio/minio:RELEASE.2024-01-16T16-07-38Z    Up (healthy)
iceberg-rest    tabulario/iceberg-rest:0.10.0                Up
spark-iceberg   tabulario/spark-iceberg:3.5.1_1.5.2         Up
trino           trinodb/trino:435                            Up
```

Si algun servicio no aparece como `Up`, espera 30 segundos mas y ejecuta `make status` de nuevo.

---

## Paso 2: Explorar MinIO

Abre el navegador en **http://localhost:9001**
Credenciales: `admin` / `password123`

1. Ve a **Buckets** en el menu lateral.
2. Deberias ver dos buckets: `warehouse` y `raw`.
   - `warehouse` es donde Iceberg almacenara las tablas (Bronze, Silver, Gold).
   - `raw` esta disponible para datos de entrada si se quisiera usar en lugar de montar el directorio local.
3. Haz clic en `warehouse` → esta vacio por ahora (las tablas se crean cuando corremos el pipeline).

---

## Paso 3: Explorar Trino UI

Abre **http://localhost:8085** en el navegador.

1. Deberias ver el dashboard de Trino con:
   - **Workers activos**: 1 (modo single-node para el taller)
   - **Running queries**: 0 (aun no ejecutamos nada)
2. Ve a la pestana **Query Detail** — estara vacia por ahora.
3. Haz clic en **Catalogs** en el menu. Deberia aparecer `iceberg` como catalogo disponible.

---

## Paso 4: Abrir Jupyter

Abre **http://localhost:8888** en el navegador.

1. En el explorador de archivos navega a `mine/` → deberia aparecer `taller6.ipynb`.
2. Abre el notebook pero **no ejecutes ninguna celda todavia** — el catalogo esta vacio.
3. Observa la estructura del notebook: tiene celdas de codigo y celdas de markdown explicativas.

---

## Paso 5: Verificar la configuracion de Trino (opcional)

Puedes revisar como Trino esta configurado para conectarse a Iceberg:

```bash
cat config/trino/catalog/iceberg.properties
```

Observa que apunta al REST catalog en `http://rest:8181` y a MinIO en `http://minio:9000`.
Esta es la razon por la que Trino puede leer las mismas tablas que Spark escribe.

---

## Preguntas de reflexion

1. ¿Cuantos servicios tiene este entorno? ¿Que hace cada uno? Completa la tabla:

   | Servicio     | Puerto | Rol en el sistema |
   |--------------|--------|-------------------|
   | minio        | 9000/9001 | |
   | iceberg-rest | 8181 | |
   | spark-iceberg | 8888/8080 | |
   | trino        | 8085 | |

2. ¿Que rol juega el REST catalog entre Spark y Trino? ¿Que pasaria si el catalogo no existiera
   y cada motor accediera directamente a los archivos en MinIO?

3. En el archivo `config/trino/catalog/iceberg.properties`, ¿por que se configura la misma
   endpoint de MinIO que usa Spark? ¿Que significa esto sobre quien tiene acceso al storage?

---

## Evidencia minima

Captura de pantalla del navegador mostrando:
- MinIO UI con los dos buckets (`warehouse` y `raw`).
- Trino UI con al menos 1 worker activo.
- Salida de `make status` con todos los servicios en estado `Up`.
