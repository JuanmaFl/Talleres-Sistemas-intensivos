# Lab 3: ACID con Iceberg — UPDATE y DELETE

## Objetivo

Ejecutar operaciones de modificacion de datos (`UPDATE` y `DELETE`) sobre una tabla Iceberg y verificar que:
1. Las operaciones funcionan sin reescribir todo el dataset
2. Cada operacion crea un nuevo snapshot preservando el historial
3. Los archivos previos permanecen en MinIO (habilitando time travel)

---

## Tiempo estimado

25 minutos

---

## Prerequisitos

- Lab 2 completado (tabla `demo.taller5.ventas` creada con 50 registros)
- MinIO Console abierta en paralelo para observar los cambios

---

## Parte A: UPDATE transaccional

### Paso 1: Ver los datos antes del UPDATE

Antes de ejecutar la celda de UPDATE, ir a MinIO Console → `warehouse/taller5/ventas/` y **contar los archivos** en las carpetas `data/` y `metadata/`. Anotar el numero.

### Paso 2: Ejecutar el UPDATE

Ejecutar la **celda 8** del notebook (UPDATE de precio de Laptop).

Output esperado:
- Los precios de Laptop antes del UPDATE: valores originales (1,500,000; 1,450,000; 1,480,000; 1,520,000; 1,490,000)
- Mensaje: `UPDATE ejecutado — nuevo snapshot creado`
- Los precios de Laptop despues del UPDATE: todos en 1,300,000

### Paso 3: Explorar MinIO despues del UPDATE

Ir a MinIO Console y actualizar la vista.

Observar que:
- En `data/` aparecio al menos **un archivo Parquet nuevo** — contiene las filas de Laptop con el precio actualizado
- En `metadata/` aparecieron nuevos archivos: un nuevo `table-metadata`, un nuevo manifest list y un nuevo manifest file
- Los archivos **anteriores siguen ahi** — no se borraron

> **Concepto clave:** Iceberg en modo Copy-on-Write reescribe solo los archivos que contienen filas afectadas. El nuevo snapshot apunta a: los archivos viejos (con las filas no modificadas) + el nuevo archivo (con las filas de Laptop actualizadas).

---

## Parte B: DELETE transaccional

### Paso 4: Ejecutar el DELETE

Ejecutar la **celda 9** del notebook.

La condicion del DELETE es `cantidad = 1 AND precio_unitario < 20000`. En el dataset de ventas, ningun registro cumple ambas condiciones simultaneamente (los productos de precio < 20000 no existen en este dataset), por lo que el DELETE no elimina filas pero **igual crea un nuevo snapshot** — esto es correcto y esperado.

> **Para una demostracion mas visual:** Puedes modificar la condicion del DELETE en el notebook a `WHERE region = 'Bogota' AND categoria = 'Perifericos'` para eliminar algunos registros reales. Verifica cuantos seran antes de ejecutar.

### Paso 5: Ver el historial de snapshots

Ejecutar la **celda 9** hasta el final — muestra la tabla `.history` con todos los snapshots.

Deben verse **3 snapshots** con las siguientes operaciones:
1. `append` — creacion inicial de la tabla
2. `overwrite` — resultado del UPDATE
3. `delete` o `overwrite` — resultado del DELETE

---

## Parte C: Analisis de los archivos en MinIO

### Paso 6: Contar los archivos

En MinIO Console, contar el total de archivos en `warehouse/taller5/ventas/`:
- `data/`: cuantos archivos `.parquet` existen ahora vs. al inicio
- `metadata/`: cuantos archivos de metadatos existen ahora vs. al inicio

Cada operacion de escritura agrega:
- 0 o mas archivos nuevos en `data/`
- 1 manifest file nuevo
- 1 manifest list nuevo
- 1 table metadata nuevo

---

## Preguntas de analisis

1. **¿Cuantos snapshots** hay en `demo.taller5.ventas.history` despues de las dos operaciones? ¿Por que hay exactamente ese numero?

2. **¿Que diferencia hay** entre los archivos en `data/` antes y despues del UPDATE? ¿Se borraron los archivos originales?

3. Si el UPDATE modifico 5 filas de Laptop y el dataset tiene 50 filas en total, **¿cuantas filas se reescribieron fisicamente** en el nuevo archivo Parquet? (Pista: depende de como esten distribuidas las filas en los archivos fisicos — en nuestro caso todos los registros estan en un solo archivo)

4. En una tabla de produccion con **10,000 archivos Parquet** de 100 MB cada uno, y un UPDATE que afecta filas en 20 de esos archivos, ¿cuantos archivos Parquet nuevos crea Iceberg? ¿Cuantos archivos viejos permanecen hasta la siguiente expiracion de snapshots?

5. **¿Por que el DELETE no borra inmediatamente los archivos Parquet** con los registros eliminados? ¿Que implicacion tiene esto para el espacio en disco?

---

## Reto opcional

Ejecutar el siguiente comando SQL en una nueva celda del notebook:

```python
spark.sql("""
    CALL demo.system.expire_snapshots(
        table => 'taller5.ventas',
        older_than => TIMESTAMP '2099-01-01 00:00:00',
        retain_last => 1
    )
""").show()
```

Despues de ejecutarlo, ir a MinIO y observar cuantos archivos quedan. ¿Que paso con los archivos de los snapshots anteriores?

> **Advertencia:** Despues de expirar snapshots, el time travel a esos snapshots ya no sera posible. Este comando es destructivo — en produccion se usa con politicas de retencion cuidadosas.

---

## Evidencia minima

- Captura de MinIO mostrando la carpeta `data/` con multiples archivos Parquet despues del UPDATE
- Output de `SELECT * FROM demo.taller5.ventas.history` mostrando los snapshots con sus operaciones
- Precios de Laptop antes y despues del UPDATE (output de las dos consultas de la celda 8)
