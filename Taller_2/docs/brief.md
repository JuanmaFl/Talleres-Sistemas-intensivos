# Project Brief: Taller Hadoop para Sistemas Intensivos en Datos

## Executive Summary

Se propone un repositorio docente para un taller introductorio de Hadoop enfocado en levantar un cluster local y ejecutar un proceso batch de `wordcount`. El objetivo es traducir conceptos del curso a una experiencia práctica, visible y reproducible.

## Problem Statement

Los estudiantes suelen entender de forma teórica conceptos como HDFS, procesamiento distribuido y batch vs streaming, pero no siempre logran conectarlos con una arquitectura operativa. El primer contacto con Hadoop además suele ser costoso por la complejidad de instalación y coordinación de servicios.

## Proposed Solution

El taller encapsula un cluster Hadoop mínimo en Docker Compose y lo acompaña con guías paso a paso. La solución minimiza fricción operativa para que el foco esté en entender roles de componentes, flujo de datos y ejecución de jobs batch.

## Target Users

### Primary User Segment: Estudiantes del curso

Estudiantes de nivel introductorio o intermedio en sistemas intensivos en datos que necesitan una primera experiencia práctica con cluster distribuido, HDFS y MapReduce.

### Secondary User Segment: Docente o monitor

Instructor que requiere una base reproducible para demostraciones en vivo, prácticas guiadas y extensiones futuras del curso.

## Goals & Success Metrics

### Business Objectives

- Reducir el tiempo de preparación técnica del laboratorio a menos de 15 minutos.
- Entregar una práctica ejecutable en computadores personales o laboratorios con Docker.
- Crear una base extensible para futuros talleres de Spark, ingestión o streaming.

### User Success Metrics

- El estudiante levanta el cluster correctamente.
- El estudiante carga archivos en HDFS sin apoyo externo.
- El estudiante ejecuta `wordcount` y explica el resultado.

### Key Performance Indicators (KPIs)

- Tasa de equipos que completan el laboratorio: al menos 80%.
- Tiempo promedio hasta el primer job exitoso: menos de 30 minutos.
- Número de incidencias operativas críticas por sesión: máximo 2.

## MVP Scope

### Core Features (Must Have)

- Cluster Hadoop mínimo con HDFS y YARN.
- Scripts de arranque y validación.
- Dataset pequeño para laboratorio.
- Guías de laboratorio y guía docente.
- Ejecución de `wordcount` usando ejemplo oficial de Hadoop.

### Out of Scope for MVP

- Desarrollo de jobs personalizados en Java.
- Integración con Spark, Hive o Kafka.
- Despliegue en nube o Kubernetes.
- Monitoreo avanzado o métricas persistentes.

### MVP Success Criteria

El taller se considera exitoso si permite a una cohorte nueva montar un cluster funcional, explorar HDFS y completar un proceso batch de `wordcount` durante una sesión de clase.

## Post-MVP Vision

### Phase 2 Features

Agregar un job propio en Java, un ejercicio de tuning de replicación y una comparación con Spark.

### Long-term Vision

Convertir el repositorio en una secuencia de laboratorios sobre almacenamiento distribuido, procesamiento batch y streaming para el curso completo.

### Expansion Opportunities

Extender el taller hacia ingestión con Kafka, almacenamiento en formato columnar y procesamiento analítico con Spark.

## Technical Considerations

### Platform Requirements

- **Target Platforms:** macOS, Linux y laboratorios con Docker Desktop
- **Browser/OS Support:** cualquier navegador moderno para interfaces de Hadoop
- **Performance Requirements:** cluster funcional en una maquina con al menos 8 GB de RAM para contenedores

### Technology Preferences

- **Frontend:** no aplica
- **Backend:** shell scripts y configuracion de contenedores
- **Database:** no aplica
- **Hosting/Infrastructure:** Docker Compose con imagenes Hadoop preconfiguradas

### Architecture Considerations

- **Repository Structure:** monorepo simple orientado a laboratorio
- **Service Architecture:** cluster distribuido de servicios Hadoop
- **Integration Requirements:** Docker y navegador web
- **Security/Compliance:** deshabilitar permisos HDFS estrictos para reducir friccion en entorno academico

## Constraints & Assumptions

### Constraints

- **Budget:** debe ejecutarse localmente sin infraestructura paga
- **Timeline:** una sesion de clase de 2 a 3 horas
- **Resources:** hardware limitado de estudiantes
- **Technical:** dependencia en Docker y compatibilidad de arquitectura de imagenes

### Key Assumptions

- Los estudiantes conocen comandos basicos de terminal.
- El docente puede dedicar unos minutos iniciales a validar Docker.
- El dataset inicial debe ser pequeño para enfocarse en conceptos.

## Risks & Open Questions

### Key Risks

- **Compatibilidad de arquitectura:** en Apple Silicon puede requerirse emulacion `amd64`.
- **Recursos insuficientes:** equipos con poca RAM pueden degradar la experiencia.
- **Friccion inicial:** errores de Docker o puertos ocupados pueden retrasar el inicio.

### Open Questions

- ¿El taller se ejecutara en equipos personales o en laboratorio institucional?
- ¿Se desea una segunda practica con jobs personalizados?
- ¿Se evaluara individualmente o por grupos?

### Areas Needing Further Research

- Escalar el laboratorio a 3 o 4 DataNodes.
- Integrar observabilidad ligera para seguir jobs en vivo.

## Next Steps

1. Validar el laboratorio en una maquina de prueba del curso.
2. Ajustar la memoria de Docker segun el entorno docente.
3. Definir rubric o evidencia de entrega para estudiantes.
