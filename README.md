# Proyecto Grupo 9 — MCDI500

Análisis de la morosidad en las patentes por no uso de derechos de aprovechamiento de aguas en Chile, a partir del conjunto de datos oficial publicado en el Portal de Datos Abiertos del Gobierno de Chile. El objetivo es describir cómo se distribuyen la morosidad y el saldo impago según Tesorería Regional, tipo de titular (persona natural o jurídica) y año de emisión, con un flujo de trabajo trazable y reproducible.

Proyecto transversal del curso *Programación para la Ciencia de Datos* (MCDI500), Magíster en Ciencia de Datos e Inteligencia Artificial, Universidad Andrés Bello.

## Integrantes

- Christian Abarca Araya (@cabarca03)
- Vicente Agosin Orellana (@VicenteAO-1)
- Patricia Campos Tapia (@patycampost)
- Daniel Valdivia Tapia (@Daniel-Val01)

## Datos

- **Fuente:** Tesorería General de la República. (2025). *tb_patentes_aguas* [Conjunto de datos]. Portal de Datos Abiertos del Gobierno de Chile. https://datos.gob.cl/dataset/tb-patentes-aguas
- **Archivo:** `F1/data/raw/tb_patentes_aguas_december_2025_data.csv` (corte a diciembre de 2025).
- **Tamaño:** 46.467 registros y 21 variables (aprox. 12 MB).
- **Licencia o condiciones de uso:** [Licencia].
- **Versionado:** el CSV se incluye en el repositorio porque pesa bastante menos que el límite de GitHub (50 MB). No es necesario descargarlo aparte.
- **Integridad:** el archivo de `data/raw/` no se modifica nunca. Su hash SHA-256 permite verificar que es el original:

      sha256sum F1/data/raw/tb_patentes_aguas_december_2025_data.csv
      # SHA-256 esperado: f62e813e539172912c81adb73fb46a61040e793aeb30de7a764eae8b04064a30

## Estructura del repositorio

    proyecto-grupo9-mcdi500/
    ├─ F1/   Definición del problema y entorno reproducible
    │  ├─ data/raw/         datos originales, sin modificar
    │  ├─ data/processed/   datos tras limpieza y transformación
    │  ├─ notebooks/        F1_Definicion.ipynb
    │  ├─ src/              funciones reutilizables (.py)
    │  └─ docs/             documentación y referencias
    ├─ F2/   Obtención, limpieza y transformación de datos
    ├─ F3/   Núcleo algorítmico: programación estructurada, recursiva y POO
    ├─ F4/   Análisis, visualización y comunicación de resultados
    ├─ requirements.txt
    ├─ .gitignore
    └─ README.md

## Requisitos y ejecución

Python 3.13

**1. Clonar el repositorio**

    git clone https://github.com/VicenteAO-1/proyecto-grupo9-mcdi500.git
    cd proyecto-grupo9-mcdi500

**2. Crear y activar el entorno virtual**

    python -m venv .venv
    source .venv/Scripts/activate      # Windows, Git Bash
    # .venv\Scripts\Activate.ps1       # Windows, PowerShell
    # .venv\Scripts\activate.bat       # Windows, cmd
    # source .venv/bin/activate        # macOS y Linux

**3. Instalar dependencias, limpieza de notebooks y kernel**

    python -m pip install -r requirements.txt
    python -m nbstripout --install
    python -m ipykernel install --user --name grupo9_mcdi500 --display-name "Python (grupo9-mcdi500)"

**4. Abrir JupyterLab desde la raíz del proyecto**

    python -m jupyterlab

En cada notebook, elegir el kernel **Python (grupo9-mcdi500)** y ejecutar los notebooks en orden (F1 → F4) desde la raíz del proyecto.

> Nota para Windows: si un comando como `nbstripout` o `jupyter kernelspec` responde *Permission denied* o *Acceso denegado*, ejecútelo como módulo de Python (`python -m nbstripout`, `python -m jupyterlab`).

## Convención de commits

Prefijos del curso, con la descripción en presente y **sin tildes ni caracteres especiales**:

| Prefijo | Uso | Ejemplo |
|---|---|---|
| `docs` | Documentación, README, informe | `docs: documenta criterios de limpieza en el README` |
| `data` | Cambios en los datos o su procesamiento | `data: incorpora dataset original en F1/data/raw` |
| `feat` | Funcionalidad o análisis nuevo | `feat: notebook F1 con perfilamiento de nulos` |
| `fix` | Corrección de un error | `fix: corrige lectura de montos con separador de miles` |

Ramas por fase y tema (por ejemplo, `f2-limpieza-datos`), integradas a `main` mediante Pull Request revisado por otro integrante.

**Flujo diario:** `git pull` antes de empezar → trabajar → `git status` → `git add <archivo>` → `git commit -m "..."` → `git push`.

## Decisiones técnicas

- **Datos originales inmutables.** El CSV de `F1/data/raw/` no se edita. Toda limpieza se programa en los notebooks y sus resultados se guardan en `data/processed/`, para que cualquier transformación pueda verificarse contra el original.
- **Registros incompletos conservados.** Los 691 registros sin año de patente y las filas con tesorería no identificada se mantienen en `data/raw/`. El criterio para tratarlos (imputar o excluir) se documentará en el notebook de F2, con su motivo e impacto.
- **CSV versionado.** Al pesar cerca de 12 MB, se incluye en el repositorio para que el proyecto pueda ejecutarse completo sin pasos adicionales.
- **Notebooks sin salidas en Git.** `nbstripout` elimina las salidas antes de cada commit, para evitar diffs ilegibles y conflictos. Antes de entregar, cada notebook debe correr completo con *Restart Kernel and Run All Cells*.
- **`.gitignore` para equipos mixtos.** Excluye el entorno virtual, cachés, checkpoints de Jupyter, archivos de sistema de Windows y macOS, y archivos de bloqueo de LibreOffice y Excel.

## Uso de inteligencia artificial

El equipo utilizó herramientas de IA generativa como apoyo en la documentación y en la configuración del entorno. Las decisiones metodológicas, la verificación de resultados y el código entregado son responsabilidad de los integrantes, quienes pueden explicar cada paso del proyecto.
