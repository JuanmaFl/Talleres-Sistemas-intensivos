# Taller Spark: Datos Estructurados con DataFrames y Parquet

Cuarto taller de la serie **Sistemas Intensivos en Datos**. El objetivo es salir
del modelo key-value de MapReduce y trabajar con la API de alto nivel de Spark:
DataFrames, Spark SQL y el formato columnar Parquet.

---

## Objetivos de aprendizaje

Al finalizar este taller el estudiante podra:

1. Leer datos estructurados en CSV con schema inferido automaticamente.
2. Aplicar transformaciones sobre DataFrames (nuevas columnas, filtros, agregaciones).
3. Escribir resultados en formato Parquet y entender sus ventajas sobre CSV.
4. Consultar DataFrames con Spark SQL usando una TempView.
5. Explicar los conceptos de lazy evaluation, column pruning y predicate pushdown.

---

## Estructura del repositorio

```
Taller_4/
├── docker-compose.yml         # Cluster Spark Standalone + Jupyter
├── Makefile                   # Comandos rapidos
├── data/
│   └── ventas.csv             # Dataset: 50 registros de ventas ficticias
├── jobs/
│   └── analisis_ventas.py     # Job de referencia (no modificar)
├── scripts/
│   ├── run-job.sh             # Ejecuta el job de referencia con spark-submit
│   └── status.sh              # Muestra estado del cluster y URLs
├── notebooks/                 # Carpeta para los notebooks del estudiante
├── labs/
│   ├── lab-01-cluster-setup.md
│   ├── lab-02-dataframes.md
│   ├── lab-03-parquet.md
│   └── lab-04-sql.md
└── docs/
    ├── brief.md
    ├── architecture.md
    └── instructor-guide.md
```

---

## Requisitos

| Herramienta | Version minima |
|---|---|
| Docker Desktop | 24+ |
| Docker Compose | v2 (incluido en Docker Desktop) |
| RAM disponible | 6 GB |
| CPU | 2 cores libres |

---

## Inicio rapido

```bash
# 1. Levantar el cluster
make up

# 2. Verificar que todos los servicios estan activos
make ps

# 3. Abrir Jupyter Lab en el navegador
#    URL: http://localhost:8888
#    Token: taller4
make notebook
```

Crea un nuevo notebook en la carpeta `work/` y sigue los labs en orden.

---

## Interfaces disponibles

| Interfaz | URL | Credenciales |
|---|---|---|
| Jupyter Lab | http://localhost:8888 | token: `taller4` |
| Spark Master UI | http://localhost:8080 | (sin autenticacion) |

---

## Flujo del taller

```
Lab 1              Lab 2               Lab 3              Lab 4
Cluster +     →   DataFrame API   →   Parquet        →   Spark SQL
Jupyter           (leer, filtrar,      (escribir,         (TempView,
                  agrupar)             leer, comparar)    queries, guardar)
```

---

## Comandos utiles

```bash
# Levantar el cluster
make up

# Ver estado de los contenedores
make ps

# Ver logs del master y Jupyter
make logs

# Ejecutar el job de referencia con spark-submit
make run-job

# Ver URLs de las interfaces
make status

# Bajar el cluster
make down

# Bajar y limpiar volumenes
make clean
```

---

## Ejecutar el job de referencia

El archivo `jobs/analisis_ventas.py` es una implementacion completa de referencia.
Los estudiantes no deben modificarlo; sirve para comparar con el trabajo hecho
en el notebook.

```bash
make run-job
```

El job:
1. Lee `ventas.csv` con schema inferido.
2. Calcula la columna `total`.
3. Agrupa por region y por producto.
4. Guarda en Parquet en `/tmp/ventas_parquet`.
5. Crea una TempView y lanza una query SQL.

---

## Material docente incluido

| Archivo | Descripcion |
|---|---|
| `docs/brief.md` | Contexto del problema y objetivos |
| `docs/architecture.md` | Diagrama y decisiones de diseno |
| `docs/instructor-guide.md` | Agenda, conceptos clave y errores frecuentes |

---

## Hilo conductor de la serie

| Taller | Tecnologia | Pregunta central | Novedad frente al anterior |
|---|---|---|---|
| 2 | HDFS + MapReduce | ¿Como distribuir almacenamiento y computo? | Primer acercamiento a Big Data |
| 3 | HDFS + Spark RDD | ¿Puede Spark reemplazar MapReduce? | Motor en memoria, misma abstraccion key-value |
| **4** | **Spark DataFrame + Parquet** | **¿Como trabajar con datos estructurados a escala?** | **API de alto nivel, formato columnar** |
| 5 | MinIO + Iceberg | ¿Como gestionar tablas en un data lake real? | Object storage + open table format |

---

## Dataset

`data/ventas.csv` — 50 registros de ventas ficticias en Colombia (2024).

Columnas: `id`, `fecha`, `producto`, `categoria`, `cantidad`, `precio_unitario`, `region`

Productos: Laptop, Monitor, Teclado, Mouse, Auriculares, Webcam, Disco SSD, RAM, Tablet, Smartphone

Regiones: Bogota, Medellin, Cali, Barranquilla, Bucaramanga

Precios en COP (pesos colombianos).
