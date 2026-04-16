# Lab 1: Levantar el entorno y explorar MinIO

## Objetivo

Levantar el cluster de cuatro servicios (MinIO, REST catalog, Spark, Jupyter) y verificar que todos los componentes estan operativos antes de ejecutar codigo.

---

## Tiempo estimado

20 minutos

---

## Prerequisitos

- Docker Desktop instalado y corriendo (minimo 6 GB de RAM asignada a Docker)
- Acceso al directorio del taller (`Taller_5/`)
- Puertos 8888, 8080, 9000, 9001, 8181 libres en la maquina local

---

## Paso 1: Levantar el cluster

Desde el directorio raiz del taller, ejecutar:

```bash
make up
```

Esto ejecuta `docker compose up -d` con los cuatro servicios. La primera vez, Docker descarga las imagenes (puede tardar varios minutos segun la velocidad de internet). Las imagenes pesan aproximadamente:

- `minio/minio`: ~120 MB
- `tabulario/iceberg-rest`: ~200 MB
- `tabulario/spark-iceberg`: ~1.5 GB (incluye Spark, JDK, Python y todos los JARs de Iceberg)

---

## Paso 2: Verificar el estado

Esperar aproximadamente 60 segundos y luego verificar:

```bash
make status
```

o directamente:

```bash
docker compose ps
```

Todos los servicios deben mostrar estado `Up` o `running`. El servicio `mc` puede aparecer como `Exited (0)` — esto es normal, su trabajo era crear los buckets al inicio y ya termino.

Para ver los logs si algo falla:

```bash
make logs
```

---

## Paso 3: Explorar la MinIO Console

Abrir en el navegador: **http://localhost:9001**

Credenciales:
- Usuario: `admin`
- Contrasena: `password123`

Una vez dentro:

1. Hacer clic en **Object Browser** en el menu lateral
2. Deben existir dos buckets:
   - `warehouse` — donde Iceberg guardara las tablas (datos + metadatos)
   - `data` — bucket auxiliar disponible para uso libre
3. El bucket `warehouse` debe estar **vacio** por ahora — todavia no hemos ejecutado nada

> **Tomar nota:** Este estado inicial (bucket vacio) es el punto de partida. En los labs siguientes volveras aqui despues de cada operacion para ver que archivos aparecieron.

---

## Paso 4: Abrir Jupyter

Abrir en el navegador: **http://localhost:8888**

En la interfaz de Jupyter:

1. Navegar a la carpeta `mine/`
2. Abrir el archivo `taller5.ipynb`
3. Verificar que el kernel de Python esta activo (circulo verde en la esquina superior derecha)

---

## Paso 5: Ejecutar la SparkSession

Ejecutar la **celda 2** del notebook (la que crea la SparkSession).

Output esperado:
```
SparkSession creada con catalogo Iceberg REST
Version de Spark: 3.5.1
```

Si aparece el mensaje sin errores, el motor Spark se comunica correctamente con el catalogo REST y esta listo para escribir en MinIO.

> **Si hay errores de conexion:** El servicio REST puede necesitar unos segundos mas. Esperar 30 segundos y volver a ejecutar la celda.

---

## Verificacion de interfaces

Una vez completados los pasos anteriores, confirmar que las siguientes URLs responden:

| Interfaz | URL | Estado esperado |
|----------|-----|----------------|
| Jupyter Notebook | http://localhost:8888 | Interfaz de Jupyter abierta |
| Spark UI | http://localhost:8080 | Dashboard de Spark (puede tardar hasta que se ejecute la primera accion) |
| MinIO Console | http://localhost:9001 | Login de MinIO |
| Iceberg REST API | http://localhost:8181/v1/config | JSON con configuracion del catalogo |

---

## Preguntas de analisis

Responder en el cuaderno de laboratorio o en el espacio asignado:

1. **¿Que es MinIO?** ¿En que se diferencia de HDFS (que usamos en los Talleres 2 y 3)?

2. **¿Que es un catalogo Iceberg?** ¿Por que es necesario un componente separado (iceberg-rest) ademas del motor de computo (Spark)?

3. **¿Por que el bucket `warehouse` empieza vacio** si ya se ejecuto la SparkSession? ¿Cuando se van a crear los primeros archivos?

4. La imagen `tabulario/spark-iceberg:3.5.1_1.5.2` pesa ~1.5 GB. ¿Por que es tan grande comparada con la imagen de MinIO (~120 MB)?

---

## Evidencia minima

- Captura de pantalla de la MinIO Console mostrando los dos buckets (`warehouse` y `data`) con el bucket `warehouse` vacio
- Captura de pantalla del output de la celda de SparkSession mostrando el mensaje de exito
