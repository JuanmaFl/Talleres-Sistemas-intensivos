# Laboratorio 1: Levantar el Cluster

## Objetivo

Levantar el cluster Hadoop local y reconocer el rol de sus componentes principales.

## Antes de empezar

- Verifica que Docker este encendido.
- Abre una terminal en la raiz del repositorio.

## Pasos

1. Levanta el cluster:

   ```bash
   make up
   ```

2. Revisa que los servicios esten activos:

   ```bash
   make ps
   ```

3. Abre estas interfaces:

   - `http://localhost:9870`
   - `http://localhost:8088`
   - `http://localhost:19888`

4. Identifica visualmente:

   - NameNode
   - DataNodes
   - ResourceManager
   - NodeManagers

## Preguntas de analisis

- ¿Que componente administra los metadatos de HDFS?
- ¿Que componente decide donde correr un job?
- ¿Por que hay mas de un nodo de datos?

## Evidencia minima

- Captura de `make ps`
- Captura de la interfaz del NameNode
