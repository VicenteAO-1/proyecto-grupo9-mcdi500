# Fase 3 — Núcleo algorítmico, eficiencia y POO

Reorganiza el procesamiento de la Fase 2 en módulos y clases sin cambiar su resultado: el pipeline de clases reproduce el archivo procesado de F2 (46.433 filas × 31 columnas).

## Contenido de la carpeta `F3/`

| Archivo | Qué es |
| --- | --- |
| `notebook_f3.ipynb` | Notebook de la fase (carga, pipeline de clases, comparación con F2, estrategias, partición, salidas para F4) |
| `notebook_f3.html` | Versión ejecutada del notebook, con sus salidas |
| `mediciones.md` | Mediciones de tiempo y memoria (bucle vs vectorizado, diccionario vs `groupby`) |
| `arquitectura.md` | Documentación de la arquitectura, patrón Strategy y escalabilidad |
| `README.md` | Este archivo |

El código reutilizable está en `src/` (raíz del proyecto):

| Módulo | Responsabilidad |
| --- | --- |
| `src/carga.py` | Cargar y limpiar el crudo; describir y guardar las salidas para F4 |
| `src/transformadores.py` | Clase base `Transformador`, estrategias del año y los cuatro transformadores |
| `src/pipeline.py` | `Pipeline` y la fábrica `crear_pipeline_f2` |
| `src/medicion.py` | Mediciones de tiempo (`timeit`) y memoria (`tracemalloc`) |
| `src/recursion.py` | Función recursiva que revisa los metadatos y detecta campos vacíos o pendientes |
| `src/utilidades.py` | Utilidades compartidas (de F1) |

## Cómo ejecutar el notebook

1. Dejar el archivo crudo en `data/raw/tb_patentes_aguas_december_2025_data.csv` (no está en el repositorio porque contiene RUT; ver el README de la raíz).
2. Crear y activar el entorno, e instalar las dependencias:

       python -m venv .venv
       source .venv/Scripts/activate      # Windows (Git Bash)
       source .venv/bin/activate          # macOS / Linux
       pip install -r requirements.txt

3. Abrir `F3/notebook_f3.ipynb` con JupyterLab y ejecutar *Restart & Run All*.

Para correr las mediciones y la revisión de metadatos por separado, desde la raíz del proyecto:

    python src/medicion.py
    python src/recursion.py

## Salidas

El notebook guarda en `data/processed/`: `entrenamiento_f3.csv`, `prueba_f3.csv`, `diccionario_f3.csv` y `parametros_f3.csv`. La partición es estratificada por `moroso`, con semilla 42 y 20 % para prueba. Son las entradas de la Fase 4.

## Dependencias

Están fijadas en `requirements.txt` de la raíz (pandas, numpy, scikit-learn, matplotlib, nbstripout, jupyterlab, entre otras).

## Reglas de trabajo del equipo

Una rama por tarea, *pull request* revisado por otro integrante, sin escritura directa en `main`. Los notebooks se guardan sin salidas (`nbstripout`); la versión ejecutada se publica como HTML.
