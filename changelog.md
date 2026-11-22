# Changelog — Proyecto Grupo 9 (MCDI500)

Registro de cambios por fase. Cada fila indica fecha, descripción, commit y justificación técnica.
Los commits de F1 a F3 son los del historial de `main`. Los de F4 son los commits reales de cada rama, integrados en `main` mediante los pull requests #7 a #10.

## Fase 1: definición y entorno reproducible

| Fecha | Descripción | Commit | Justificación técnica |
|---|---|---|---|
| 2026-11-08 | Estructura inicial, README, requirements y .gitignore | `a71040b` | Base reproducible desde el primer día |
| 2026-11-11 | Se retiran del repositorio los datos originales con RUT | `88bc28c` | Protección de datos personales; `data/raw/` queda fuera de Git |
| 2026-11-11 | Un solo notebook F1, rutas relativas y diccionario corregido | `d7d6705` | El notebook corre en cualquier equipo |
| 2026-11-11 | Módulo `src` y artefactos generados por F1 | `74c9373` | Primera separación entre código reutilizable y notebook |

## Fase 2: limpieza y transformación

| Fecha | Descripción | Commit | Justificación técnica |
|---|---|---|---|
| 2026-11-11 | Se sube F2: exploración, limpieza y análisis | `3c4bc4b` | Preprocesamiento documentado y trazable |
| 2026-11-17 | Se quita el escalamiento del procesamiento descriptivo | `76ac9ed` | Las tasas y medianas se interpretan en unidades originales |
| 2026-11-17 | Se agrega la variable `moroso` | `179ccd6` | Variable objetivo `SALDO > 0` |
| 2026-11-17 | Se restaura F2 con `moroso` y `anio_faltante` | `e950869` | Se resuelven conflictos de integración |

## Fase 3: núcleo algorítmico

| Fecha | Descripción | Commit | Justificación técnica |
|---|---|---|---|
| 2026-11-18 | Clase base `Transformador`, transformadores y `Pipeline` | `d6b1ac1` | POO: herencia, polimorfismo y encapsulamiento |
| 2026-11-18 | Partición entrenamiento y prueba estratificada | `8d77ab3` | Evaluación sin fuga; insumo de la Fase 4 |
| 2026-11-18 | Mediciones de tiempo y memoria (PR #2) | `6d7a518` | Comparación formal con `timeit` y `tracemalloc` |
| 2026-11-18 | Recursión y documentación de arquitectura (PR #3) | `561f8ad` | Búsqueda recursiva de metadatos pendientes |
| 2026-11-18 | Pruebas unitarias de transformadores y pipeline (PR #4) | `d6dac26` | 32 pruebas, incluida la equivalencia exacta con F2 |
| 2026-11-18 | Declaración de uso de IA (PR #6) | `b86d766` | Integridad académica |

## Fase 4: análisis, reproducibilidad y comunicación

Cada cambio responde a una observación de la retroalimentación de la Fase 3 (21-11-2026).

| Fecha | Descripción | Rama / commit | Justificación técnica |
|---|---|---|---|
| 2026-11-22 | `src/indicadores.py`: intervalo de Wilson, tasa por grupo y carga de la base F4 | `dc53e34` (PR #7) | Indicadores con incertidumbre y n por grupo, en un módulo con pruebas |
| 2026-11-22 | `tests/test_indicadores.py`: 8 pruebas (valor conocido, extremos, n = 0, éxitos > n, columna ausente) | `dc53e34` (PR #7) | Casos normales, límite y excepciones |
| 2026-11-22 | `F4/generar_figuras.py`: tres figuras (líneas con banda, barras con intervalos y violín con caja del monto en UTM) con título que enuncia el hallazgo, unidades y fuente | `f57be4e` (PR #9) | Figuras reproducibles por script; el año 0 no se grafica |
| 2026-11-22 | `F4/generar_diagrama.py` y `docs/arquitectura.png` | `f57be4e` (PR #9) | Documentación de la arquitectura |
| 2026-11-22 | `F3/mediciones.md` regenerado desde la ejecución del notebook F4 | `39a7fbd` (PR #8) | Las cifras de eficiencia coinciden entre informe, HTML y repositorio |
| 2026-11-22 | `F4/notebook_f4.ipynb` y `.html`: análisis, modelo con línea base y regeneración de cifras | `2d0987d` (PR #10) | Una sola ejecución alimenta informe, HTML y video |
| 2026-11-22 | `requirements.txt`: versión fija en todas las dependencias, incluidas `ipykernel`, `jupyterlab`, `notebook` y `pytest` | `2d0987d` (PR #10) | Reproducibilidad completa del entorno |

### Impacto de las mejoras

- **Modularidad:** los indicadores y las figuras salen de los notebooks y viven en `src/` y `F4/`, con pruebas.
- **Rendimiento:** la vectorización (unas 85 veces más rápida) y `groupby` (unas 4 veces) se mantienen como versiones elegidas; el diccionario queda como alternativa si la memoria fuera la restricción.
- **Documentación:** informe con fragmentos de código comentados, diagrama de arquitectura, tabla de trazabilidad y cifras con su celda de origen.
