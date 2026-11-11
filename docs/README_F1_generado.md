# consolidacion de patentes por no uso de derechos de aprovechamiento de aguas — Grupo 9

Análisis de la morosidad en las patentes por no uso de derechos de aprovechamiento de aguas en Chile, a partir del conjunto de datos oficial publicado en el Portal de Datos Abiertos del Gobierno de Chile. El objetivo es describir cómo se distribuyen la morosidad y el saldo impago según Tesorería Regional, tipo de titular (persona natural o jurídica) y año de emisión, con un flujo de trabajo trazable y reproducible. 

## Integrantes
- Christian Abarca Araya (@usuario-github)
- Vicente Agosin Orellana (@usuario-github)
- Patricia Campos Tapia (@usuario-github)
- Daniel Valdivia Tapia (@usuario-github)

## Datos
- Fuente: Consolidación de patentes por no uso de derechos de aprovechamiento de aguas (Tesorería General de la República, Portal de Datos Abiertos del Gobierno de Chile)
- Enlace: https://datos.gob.cl/dataset/tb-patentes-aguas
- Estructura: 46467 filas x 21 columnas
- Ubicación esperada: `data/raw/`

## Estructura del repositorio
```
data/raw/        datos originales, sin modificar
data/processed/  datos tras limpieza y transformación (F2)
docs/            diccionario, fichas y metadatos
src/             módulos reutilizables del proyecto
F1/ F2/ F3/ F4/  cuadernos e informes de cada fase
```

## Requisitos y ejecución
Python 3.13

    python -m venv .venv
    source .venv/Scripts/activate    # Windows, Git Bash
    # source .venv/bin/activate      # macOS y Linux
    python -m pip install -r requirements.txt

Ejecutar los cuadernos en orden, F1 y luego F2. Cada cuaderno localiza la raíz del
proyecto aunque Jupyter lo abra en su propia carpeta.

### Dependencias declaradas
- ipykernel
- jupyterlab
- jupyterlab-git
- jupytext
- matplotlib==3.11.2
- nbstripout
- notebook
- numpy==2.5.4
- pandas==3.1.1
- scikit-learn==1.9.1

## Convención de commits
Prefijos usados: docs, data, feat, fix.

## Decisiones técnicas
- Los datos son comunes a todas las fases (`data/`); los cuadernos se separan por fase.
- Semilla aleatoria fijada en 42 para asegurar reproducibilidad.
- Registro breve de las decisiones relevantes y su motivo, actualizado al cerrar cada fase.
