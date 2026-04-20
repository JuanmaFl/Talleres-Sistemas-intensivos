# Lab-01 

1. ¿Cuantos servicios tiene este entorno? ¿Que hace cada uno? Completa la tabla:

El entorno tiene 5 servicios: 
Minio es el almacenamiento de objetos compatible con S3 y guarda los archivos Parquet de las tablas Iceberg en los puertos 9000 y 9001. 
Iceberg-rest es el catálogo de metadatos que corre en el puerto 8181 y dice dónde está cada tabla, su esquema y snapshots. 
Spark-iceberg es el motor que procesa y transforma datos (ETL), lee de Bronze y escribe a Silver y Gold, corriendo en los puertos 8080 y 8888. 
Trino es un motor SQL distribuido en el puerto 8085 que permite a los analistas hacer queries sin necesidad de Spark. 
Jupyter es un notebook interactivo en el puerto 8888 que permite explorar datos con spark.

2. ¿Que rol juega el REST catalog entre Spark y Trino? ¿Que pasaria si el catalogo no existiera
   y cada motor accediera directamente a los archivos en MinIO?

El REST catalog es lo que une a Spark y Trino. Cuando Spark escribe datos, le dice al catalog dónde está la tabla y sus metadatos. Cuando Trino quiere leer datos, pregunta al catalog dónde está la tabla y obtiene su ubicación y esquema. Sin el catalog, Spark no sabría dónde guardar los metadatos y Trino no sabría que existen las tablas. Cada uno tendría su propia versión de la verdad, lo que causaría inconsistencia en los datos. El catalog es esencial para que ambos motores trabajen sobre los mismos datos.

3. En el archivo `config/trino/catalog/iceberg.properties`, ¿por que se configura la misma
   endpoint de MinIO que usa Spark? ¿Que significa esto sobre quien tiene acceso al storage?

Se configura la misma endpoint de MinIO porque los dos motores leen y escriben en el mismo lugar físico. Esto significa que no hay replicación de datos ni copias de seguridad manuales. Ambos motores ven los mismos datos instantáneamente sin necesidad de sincronización. El acceso no depende de un motor específico, lo que permite que cualquier herramienta compatible con S3 pueda acceder a los datos de Iceberg.

# lab-02

1. ¿Que columnas tiene Silver que NO tiene Bronze? Lista al menos 4.

Silver tiene cuatro columnas principales que Bronze no tiene. La primera es proveedor, que se obtiene del JOIN con la tabla dimensiones_productos. La segunda es margen_pct, que también viene del JOIN con dimensiones. La tercera es total, que se calcula multiplicando la cantidad por el precio unitario. La cuarta es ganancia, que se calcula multiplicando el total por el margen de ganancia dividido entre 100.

2. ¿Que informacion pierde Gold en comparacion con Silver? Da un ejemplo concreto:
   ¿puedes saber desde Gold el `precio_unitario` de una venta especifica?

Gold pierde el detalle de cada venta individual porque agrega los datos. En Silver puedes ver que el cliente X compró un Laptop por $1000 con $200 de ganancia el 15 de enero de 2024. En Gold solo ves que la región Bogotá, categoría Electrónica, tuvo $45000 de ingresos totales en enero. No puedes recuperar desde Gold el precio exacto de esa venta específica porque está sumado con todas las otras ventas. Es un trade-off: Silver es detallado pero voluminoso, Gold es compacto pero generalizado.

3. En MinIO, ¿cuantos archivos `.parquet` hay en `bronze_ventas/data/`?
   ¿Ese numero cambia si re-ejecutas `make ingest`? ¿Por que?

Generalmente hay 1 archivo porque 30 filas es poco volumen para Spark. Sin embargo, este número cambia si re-ejecutas el ingest porque createOrReplace borra los archivos viejos y escribe nuevos. Dependiendo del paralelismo de Spark podrían ser 1 o más archivos, pero en este caso con 30 filas esperamos 1 archivo.

4. El script `transform_silver.py` hace un join LEFT entre las ventas y las dimensiones de productos.
   ¿Que pasaria si llega una venta de un producto que no existe en `dimensiones_productos.csv`?
   ¿Que valor tendria `proveedor` en ese caso? ¿Es un problema?

Si llega una venta de un producto que no existe en dimensiones_productos, el LEFT JOIN mantiene la venta en la tabla. Sin embargo, los campos proveedor y margen_pct quedarán con valor NULL porque no hay match en la tabla de dimensiones. Esto causa que la columna ganancia también sea NULL, lo que rompe los análisis posteriores. Es un problema porque los datos quedan incompletos. El script probablemente valida que todos los productos existan en dimensiones antes del JOIN para evitar esta situación.


# lab - 03

1. Despues de ejecutar el lote 2, ¿cuantos snapshots tiene la tabla `bronze_ventas`?
   ¿Como lo verifica?

Después de ejecutar el lote 2, la tabla bronze_ventas tiene 2 snapshots. El primer snapshot tiene la operación 'overwrite' con 30 registros del lote inicial. El segundo snapshot tiene la operación 'append' con 20 registros nuevos, totalizando 50 registros. Puedes verificar esto ejecutando una query al historial de snapshots de la tabla.

2. ¿Cual es la diferencia entre `writeTo(...).append()` y `writeTo(...).createOrReplace()`
   en terminos de:
   - Numero de snapshots generados
   - Datos perdidos/preservados
   - Caso de uso tipico

El método append() agrega nuevos datos sin tocar los anteriores y genera un nuevo snapshot. Los datos viejos se preservan en snapshots anteriores. Sin embargo, no es idempotente: si ejecutas append dos veces, duplicarás los datos. El caso de uso típico es la ingestión incremental de nuevos lotes. Por otro lado, createOrReplace() reemplaza todos los datos y no genera un nuevo snapshot preservando el anterior. Es idempotente: ejecutar dos veces produce el mismo resultado. Su caso de uso típico es recalcular o refrescar todos los datos de una tabla.

3. Silver y Gold usan `createOrReplace` en lugar de `append`. ¿Por que tiene sentido esa decision?
   Pista: piensa en idempotencia y en que pasa si re-ejecutas el pipeline dos veces.

Silver y Gold usan createOrReplace por razones de idempotencia. Imagina que ejecutas el pipeline dos veces. Si Silver usara append, la primera ejecución crearía 30 filas en Silver y la segunda agregaría 30 más, resultando en 60 filas duplicadas y datos corruptos. Con createOrReplace, ambas ejecuciones generan el mismo resultado: 30 filas. Esto es crítico porque Silver y Gold son tablas derivadas que deben recalcularse completas cada vez que el pipeline se ejecuta.

4. Si quisieramos que Silver tambien mantuviera el historial (como Bronze), ¿que cambiariamos
   en `transform_silver.py`? ¿Habria algun riesgo con ese enfoque?

Si quisieras que Silver mantuviera historial como Bronze, cambiarías en transform_silver.py el método de escritura de createOrReplace() a append(). Sin embargo, el riesgo es que si ejecutas el pipeline dos veces, duplicarías todos los registros de Silver. Una mejor solución sería usar merge() (upsert de Iceberg) para actualizar registros existentes en lugar de append. La conclusión es que Bronze debe ser histórico y acumulativo con append, mientras que Silver debe ser actual y determinístico con createOrReplace.


lab - 04

1. **¿Por que Trino puede leer las tablas de Iceberg sin necesitar Spark?**
   Explica el rol del catalogo REST en este proceso. ¿Que informacion obtiene Trino del catalogo?

Trino es un motor SQL distribuido que tiene su propio cliente capaz de leer directamente archivos Parquet. Cuando ejecutas una query en Trino, primero conecta al REST catalog en el puerto 8181 y pregunta dónde está la tabla gold_metricas_region. El catalog responde con la ubicación exacta en MinIO y el schema de la tabla. Trino entonces lee directamente los archivos Parquet de MinIO usando la API S3 sin necesidad de Spark. El rol del catalog es actuar como traductor: sin él, Trino no sabría que existen las tablas ni dónde encontrarlas.

2. **¿Que rol juega el catalogo REST entre Spark y Trino?**
   ¿Que pasaria si Spark escribiera las tablas sin registrarlas en un catalogo compartido?


El catálogo REST es la fuente única de verdad entre Spark y Trino. Cuando Spark escribe una tabla, le dice al catalog la ubicación, el schema y los snapshots. Cuando Trino quiere leer esa tabla, consulta el catalog para obtener la misma información. Ambos motores acceden entonces a los mismos datos en MinIO. Sin un catalog compartido, Spark y Trino tendrían metadatos separados, lo que causaría inconsistencia: Spark podría pensar que la tabla tiene un schema diferente al que Trino ve, o incluso que la tabla está en una ubicación diferente.

3. **¿En que caso usarias Trino en lugar de Spark SQL?**
   Menciona al menos dos escenarios donde Trino es la mejor opcion y dos donde Spark lo es.

Deberías usar Trino cuando eres un analista que solo sabe SQL y necesitas hacer queries rápidas ad-hoc, como "¿cuáles fueron los ingresos por región?" sin necesidad de programar. También es ideal cuando necesitas conectar desde herramientas BI como Tableau o Power BI. Por el contrario, deberías usar Spark cuando necesitas transformaciones complejas que requieren múltiples joins, lógica condicional avanzada o cuando necesitas escribir nuevas tablas a Iceberg, ya que Spark tiene capacidades de escritura que Trino no tiene.


4. **Sobre el query plan de Trino UI**: ¿que significa que un query tenga multiples "stages"?
   ¿Como se distribuye el trabajo cuando hay un `GROUP BY`?

Un "stage" es una fase de ejecución distribuida en Trino. Por ejemplo, en un query como "SELECT region, SUM(ingresos) FROM gold GROUP BY region", el Stage 1 lee los archivos Parquet en paralelo desde todos los workers. El Stage 2 hace una suma local en cada worker por región. El Stage 3 es un shuffle que redistribuye los datos para agrupar todas las filas del mismo region en el mismo worker. El Stage 4 hace la suma final de todos los parciales. Múltiples stages son necesarios porque permiten procesar datos en paralelo de forma eficiente: sin stages, un único worker haría todo el trabajo (muy lento).


# Pregunta final

El Taller 2 usaba HDFS como storage y MapReduce como motor de procesamiento, trabajando con archivos de texto plano. El Taller 3 mejoró el motor reemplazando MapReduce con Spark, que es significativamente más rápido. El Taller 4 introdujo Parquet, un formato columnar binario que mejora compresión y hace las queries más eficientes. El Taller 5 cambió el storage de HDFS a MinIO compatible con S3 y agregó Apache Iceberg como formato de tabla, trayendo snapshots y versionado. El Taller 6 completa la evolución con la arquitectura Lakehouse, agregando tres capas de datos Bronze, Silver, Gold, un catálogo REST compartido, y múltiples motores Spark para ETL y Trino para análisis. La gran diferencia es que antes cada herramienta tenía sus propios datos y metadatos. Ahora, con el Lakehouse, todos los motores leen del mismo storage y consultan el mismo catálogo, lo que es más barato, más rápido y más confiable.