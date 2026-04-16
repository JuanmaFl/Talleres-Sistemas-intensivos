# Taller 5: Open Table Formats sobre Object Storage

**Curso:** Sistemas Intensivos en Datos
**Stack:** MinIO + Apache Spark 3.5 + Apache Iceberg 1.5

---

## Objetivos de aprendizaje

Al finalizar este taller, el estudiante sera capaz de:

1. Explicar el problema que tienen los archivos Parquet planos cuando se necesita ACID, historial de cambios o evolucion de schema
2. Crear y consultar tablas Iceberg sobre MinIO usando el catalogo REST
3. Ejecutar `UPDATE` y `DELETE` transaccionales con garantias ACID
4. Usar time travel para leer el estado de la tabla en un snapshot anterior
5. Realizar schema evolution agregando columnas sin reescribir datos historicos
6. Navegar la estructura de archivos de Iceberg en MinIO para entender como funciona por dentro

---

## Estructura del repositorio

```
Taller_5/
├── docker-compose.yml        # Servicios: MinIO, REST catalog, Spark+Iceberg, mc
├── Makefile                  # Comandos utiles: up, down, clean, status
├── README.md                 # Este archivo
│
├── data/
│   └── ventas.csv            # Dataset de 50 registros (mismo del Taller 4)
│
├── notebooks/
│   └── taller5.ipynb         # Notebook principal con 5 partes
│
├── scripts/
│   └── status.sh             # Verificacion del estado del cluster
│
├── docs/
│   ├── brief.md              # Descripcion del problema que resuelve Iceberg
│   ├── architecture.md       # Arquitectura tecnica y decisiones de diseno
│   └── instructor-guide.md   # Guia para el docente (agenda, tips, evidencias)
│
└── labs/
    ├── lab-01-cluster-setup.md      # Levantar entorno y explorar MinIO
    ├── lab-02-parquet-vs-iceberg.md # El problema de Parquet + crear tabla Iceberg
    ├── lab-03-acid.md               # UPDATE y DELETE transaccionales
    └── lab-04-time-travel.md        # Time travel y schema evolution
```

---

## Requisitos

- **Docker Desktop** instalado y corriendo
- **RAM asignada a Docker:** minimo 6 GB (recomendado 8 GB)
- **Espacio en disco:** ~3 GB (imagenes Docker)
- **Puertos libres:** 8888, 8080, 9000, 9001, 8181

---

## Inicio rapido

```bash
# 1. Levantar todos los servicios
make up

# 2. Esperar ~60 segundos para que los servicios inicien

# 3. Verificar el estado
make status

# 4. Abrir Jupyter en el navegador
# http://localhost:8888
# Navegar a mine/ → taller5.ipynb
```

---

## Interfaces disponibles

| Interfaz | URL | Credenciales |
|----------|-----|-------------|
| Jupyter + Spark | http://localhost:8888 | — |
| Spark UI | http://localhost:8080 | — |
| MinIO Console | http://localhost:9001 | admin / password123 |
| Iceberg REST API | http://localhost:8181 | — |

> **Tip pedagogico:** Mantener MinIO Console abierta mientras ejecutas el notebook. Despues de cada operacion, ver que archivos aparecen en `warehouse/taller5/ventas/`. Esto hace concreta la abstraccion de "snapshots".

---

## Flujo del taller

El notebook `taller5.ipynb` esta dividido en 5 partes que siguen una progresion logica:

```
Parte 1: El problema con Parquet plano
         ↓ (motivacion)
Parte 2: Crear tabla Iceberg → explorar estructura en MinIO
         ↓
Parte 3: ACID — UPDATE y DELETE → ver nuevos snapshots en MinIO
         ↓
Parte 4: Time Travel → leer snapshot inicial
         ↓
Parte 5: Schema Evolution → agregar columna sin reescribir datos
```

Los labs (`labs/`) van en paralelo con el notebook y agregan preguntas de analisis y retos opcionales.

---

## Comandos utiles

```bash
# Levantar el cluster
make up

# Detener (conserva los datos en el volumen de MinIO)
make down

# Detener y eliminar todos los datos (volumen minio_data)
make clean

# Ver logs de Spark y del catalogo REST
make logs

# Ver estado de todos los servicios
make status

# Ver los contenedores corriendo
make ps
```

---

## Material docente incluido

- **`docs/brief.md`** — Descripcion concisa del problema y la solucion para compartir con estudiantes antes del taller
- **`docs/architecture.md`** — Arquitectura tecnica detallada con diagrama Mermaid
- **`docs/instructor-guide.md`** — Agenda de 2.5 horas, tips de clase, errores comunes y preguntas de cierre

---

## Hilo conductor de la serie

| Taller | Stack | Concepto central |
|--------|-------|-----------------|
| Taller 2 | HDFS + MapReduce | Almacenamiento distribuido + computo batch |
| Taller 3 | HDFS + Spark | Motor de procesamiento en memoria |
| Taller 4 | Spark + DataFrames + Parquet | Formato columnar eficiente |
| **Taller 5** | **MinIO + Spark + Iceberg** | **Open Table Formats: ACID, time travel, schema evolution** |
| Taller 6 | MinIO + Iceberg + Trino | Lakehouse completo con motor SQL federado |

El mismo dataset de ventas (50 registros, mismo schema) se usa en los Talleres 4 y 5 para que el contraste entre Parquet plano e Iceberg sea inmediato y tangible.

---

## Referencia rapida de comandos Iceberg

```sql
-- Crear tabla Iceberg
CREATE TABLE demo.taller5.mi_tabla (id INT, nombre STRING) USING iceberg;

-- Insertar datos
INSERT INTO demo.taller5.mi_tabla VALUES (1, 'test');

-- UPDATE transaccional
UPDATE demo.taller5.mi_tabla SET nombre = 'nuevo' WHERE id = 1;

-- DELETE transaccional
DELETE FROM demo.taller5.mi_tabla WHERE id = 1;

-- Ver historial de snapshots
SELECT * FROM demo.taller5.mi_tabla.history;

-- Time travel por snapshot ID
SELECT * FROM demo.taller5.mi_tabla VERSION AS OF 1234567890;

-- Time travel por timestamp
SELECT * FROM demo.taller5.mi_tabla TIMESTAMP AS OF '2024-01-01 00:00:00';

-- Agregar columna (schema evolution)
ALTER TABLE demo.taller5.mi_tabla ADD COLUMN nueva_col DOUBLE;

-- Expirar snapshots antiguos (liberar espacio)
CALL demo.system.expire_snapshots('taller5.mi_tabla', TIMESTAMP '2099-01-01 00:00:00', 1);
```
