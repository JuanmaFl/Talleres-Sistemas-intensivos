# Laboratorio 3: Ejecutar WordCount

## Objetivo

Ejecutar un proceso batch distribuido usando MapReduce sobre YARN.

## Pasos

1. Ejecuta el job:

   ```bash
   make wordcount
   ```

2. Consulta la salida completa:

   ```bash
   docker compose exec -T namenode hdfs dfs -cat /user/root/wordcount/output/part-r-00000
   ```

3. Abre la interfaz del ResourceManager y revisa el estado del job.

4. Abre la interfaz del HistoryServer y busca los detalles historicos del proceso.

## Preguntas de analisis

- ¿Por que este proceso es batch?
- ¿Que hacen los mappers y reducers en este ejemplo?
- ¿Que palabra aparece con mayor frecuencia y por que?
- ¿Que cambiaria si el volumen de datos creciera 1000 veces?

## Evidencia minima

- Captura del job completado en `8088`
- Fragmento de `part-r-00000`
- Respuesta breve sobre batch vs streaming
