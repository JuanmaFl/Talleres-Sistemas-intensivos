# Lab 4: Time Travel y Schema Evolution

## Objetivo

Usar las capacidades avanzadas de Iceberg que son imposibles con Parquet plano:
1. **Time Travel**: leer el estado de la tabla en un snapshot anterior
2. **Schema Evolution**: agregar una columna sin reescribir los datos historicos

---

## Tiempo estimado

25 minutos (+ 10 min de retos opcionales)

---

## Prerequisitos

- Labs 1, 2 y 3 completados
- La tabla `demo.taller5.ventas` debe tener al menos 3 snapshots (creacion + UPDATE + DELETE)

---

## Parte A: Time Travel

### Paso 1: Ver el historial de snapshots

Ejecutar la **celda 11** del notebook.

Anotar los `snapshot_id` de cada operacion:
- ID del snapshot inicial (operacion: `append`)
- ID del snapshot del UPDATE (operacion: `overwrite`)
- ID del snapshot del DELETE (operacion: `overwrite` o `delete`)

### Paso 2: Leer el snapshot inicial

Ejecutar la **celda 12** del notebook.

Esta celda:
1. Obtiene el `snapshot_id` del primer snapshot programaticamente
2. Hace un `COUNT(*)` sobre ese snapshot
3. Compara el precio de los Laptop en el snapshot inicial vs. el estado actual

Output esperado:
- El snapshot inicial tiene **50 registros** (los mismos que el CSV original)
- Los precios de Laptop en el snapshot inicial son los originales (no 1,300,000)

### Paso 3: Escenario de recuperacion de errores

Imaginar el siguiente escenario real: un analista ejecuto el siguiente comando sin WHERE:

```sql
DELETE FROM demo.taller5.ventas
```

Esto borraria **todos** los registros. Sin Iceberg, los datos estarian perdidos hasta que se restaure un backup. Con Iceberg, la recuperacion es inmediata:

Ejecutar en una nueva celda del notebook:

```python
# Simular un DELETE masivo accidental
spark.sql("DELETE FROM demo.taller5.ventas WHERE id > 0")  # borra todo
print("DELETE masivo ejecutado (simulacion de error)")
print(f"Registros restantes: {spark.sql('SELECT COUNT(*) FROM demo.taller5.ventas').collect()[0][0]}")
```

Luego, para "recuperar" los datos del ultimo snapshot bueno:

```python
# Obtener el snapshot antes del DELETE masivo
history = spark.sql("""
    SELECT snapshot_id, operation, committed_at
    FROM demo.taller5.ventas.history
    ORDER BY committed_at DESC
""").collect()

# El segundo en la lista (el ultimo antes del DELETE masivo)
snapshot_antes_del_error = history[1].snapshot_id
print(f"Recuperando datos del snapshot: {snapshot_antes_del_error}")

# Restaurar
spark.sql(f"""
    INSERT INTO demo.taller5.ventas
    SELECT * FROM demo.taller5.ventas VERSION AS OF {snapshot_antes_del_error}
""")

print(f"Recuperados: {spark.sql('SELECT COUNT(*) FROM demo.taller5.ventas').collect()[0][0]} registros")
```

---

## Parte B: Schema Evolution

### Paso 4: Agregar columna sin reescritura

Ejecutar la **celda 14** del notebook.

Esta celda:
1. Muestra el schema ANTES (sin la columna `descuento`)
2. Ejecuta `ALTER TABLE ... ADD COLUMN descuento DOUBLE`
3. Muestra las primeras filas — la columna `descuento` aparece como `NULL`

**Lo que NO paso:**
- Los archivos Parquet en MinIO **no se reescribieron**
- El proceso fue instantaneo, independientemente del tamano del dataset
- Las queries anteriores que no usaban `descuento` **siguen funcionando sin cambios**

### Paso 5: Insertar datos nuevos con la columna poblada

Ejecutar la **celda 14b** del notebook.

Se insertan 2 registros con `descuento` diferente de NULL. Al consultar todos los registros, se ve el mix:
- Registros con `id < 51`: `descuento = NULL`
- Registros con `id >= 51`: `descuento = 0.10` o `0.05`

Ir a MinIO → `data/` — hay un nuevo archivo Parquet para los registros recientes. Los archivos viejos siguen siendo identicos y no tienen la columna `descuento` fisicamente — Iceberg resuelve el mapeo en tiempo de lectura usando los IDs internos de columnas.

---

## Retos opcionales

### Reto 1: Rollback a un snapshot especifico

Iceberg permite hacer rollback del catalogo (sin copiar datos) usando:

```python
spark.sql("""
    CALL demo.system.rollback_to_snapshot('taller5.ventas', <snapshot_id_inicial>)
""")
```

Reemplaza `<snapshot_id_inicial>` con el ID del primer snapshot. Despues del rollback:
- La tabla vuelve a tener 50 registros
- Los precios de Laptop son los originales
- Los archivos fisicos en MinIO no cambiaron

> **Nota:** El rollback no borra los snapshots posteriores — solo mueve el puntero del catalogo. Puedes volver al estado mas reciente haciendo otro rollback.

### Reto 2: Insertar datos nuevos con descuento y calcular el total ajustado

Agregar 5 filas nuevas de productos con la columna `descuento` poblada (valores entre 0.05 y 0.20), luego calcular el precio final:

```python
spark.sql("""
    SELECT
        producto,
        precio_unitario,
        descuento,
        ROUND(precio_unitario * (1 - COALESCE(descuento, 0)), 0) as precio_final
    FROM demo.taller5.ventas
    ORDER BY id DESC
    LIMIT 10
""").show()
```

### Reto 3: Time travel con timestamp

En vez de usar `VERSION AS OF <snapshot_id>`, usar:

```python
# Leer el estado de la tabla hace 10 minutos
spark.sql("""
    SELECT COUNT(*)
    FROM demo.taller5.ventas
    TIMESTAMP AS OF (current_timestamp() - INTERVAL 10 MINUTES)
""").show()
```

---

## Preguntas de analisis

1. **¿Cuando es util el time travel en produccion?** Dar al menos dos escenarios concretos distintos al error del DELETE masivo.

2. **¿Que pasaria** si en un sistema sin Iceberg quisieras "deshacer" un DELETE masivo de 5 millones de registros? Describir el proceso de recuperacion y estimar cuanto tardaria.

3. **¿Por que Schema Evolution en Iceberg no requiere reescribir los archivos Parquet** existentes? Mencionar el concepto de "IDs internos de columnas".

4. Si agregas una columna `descuento` con `ALTER TABLE`, los archivos Parquet viejos fisicamente **no contienen esa columna**. ¿Como sabe Spark que valor mostrar para esa columna en las filas antiguas?

5. En una empresa con regulaciones de privacidad (GDPR), un usuario pide "ser olvidado" — sus datos deben borrarse de todos los sistemas. Con Iceberg, ejecutas el `DELETE`. Pero el snapshot anterior todavia tiene sus datos. ¿Como manejas este caso? ¿Que operacion de Iceberg necesitas ejecutar adicionalmente?

---

## Evidencia minima

- Capturas del output de time travel mostrando: count en snapshot inicial (50 registros) vs. count actual
- Captura del output de `DESCRIBE TABLE demo.taller5.ventas` despues de agregar la columna `descuento`
- Captura mostrando filas con `descuento = NULL` (antiguas) y filas con `descuento` poblado (nuevas) en la misma consulta
- Respuestas escritas a las preguntas de analisis 1 y 2
