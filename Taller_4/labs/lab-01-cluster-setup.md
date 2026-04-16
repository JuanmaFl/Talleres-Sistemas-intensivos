# Lab 1: Levantar el cluster y abrir Jupyter

## Objetivo

Poner en marcha el cluster de Spark Standalone y verificar que los cuatro
contenedores (master, worker-1, worker-2, jupyter) estan saludables antes de
empezar a escribir codigo.

---

## Pasos

### 1. Levantar el cluster

Desde la raiz del repositorio:

```bash
make up
```

Espera entre 15 y 30 segundos mientras las imagenes arrancan. Puedes verificar
el estado con:

```bash
make ps
# o directamente:
docker compose ps
```

Todos los servicios deben mostrar estado `Up` o `running`.

### 2. Abrir Spark Master UI

Abre en el navegador:

```
http://localhost:8080
```

Deberias ver la pagina de Spark Standalone con:
- **Status:** ALIVE
- **Workers:** 2 workers registrados
- **Memory in use:** ~2 GB total (1G por worker)

### 3. Abrir Jupyter Lab

```
http://localhost:8888
```

Cuando pida el token, escribe: `taller4`

Se abrira Jupyter Lab. Navega a la carpeta `work/` y crea un nuevo notebook
de Python 3.

### 4. Crear una SparkSession desde el notebook

En la primera celda del notebook:

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("Taller4")
    .master("spark://spark-master:7077")
    .getOrCreate()
)

print("Spark version:", spark.version)
print("App name:", spark.sparkContext.appName)
```

Ejecuta la celda. La primera ejecucion puede tardar 5-10 segundos mientras
Spark conecta los executors.

### 5. Verificar en la Spark UI

Vuelve a `http://localhost:8080`. En la seccion **Running Applications** deberia
aparecer tu aplicacion `Taller4`.

---

## Preguntas

1. **¿Que diferencia hay entre ejecutar Spark en modo `local[*]` y en modo
   `spark://spark-master:7077`?**
   Piensa en donde corren los executors y quien coordina las tareas.

2. **¿Que ves en la Spark UI cuando ejecutas la primera celda del notebook?**
   Observa la seccion "Running Applications" y el numero de executors registrados.

3. **¿Cuantos cores tiene el cluster en total?** (pista: mira los workers)

---

## Evidencia minima

- Captura de pantalla de la Spark UI mostrando los 2 workers activos.
- Salida de la celda del notebook con `Spark version: 3.5.x`.
