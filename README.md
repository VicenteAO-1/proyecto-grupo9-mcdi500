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
- **Archivo:** `data/raw/tb_patentes_aguas_december_2025_data.csv` (corte a diciembre de 2025).
- **Tamaño:** 46.467 registros y 21 variables (aprox. 12 MB).
- **Licencia o condiciones de uso:** [Creative Commons CCZero (CC0 1.0 Universal)](https://creativecommons.org/publicdomain/zero/1.0/), según la ficha del dataset en datos.gob.cl.
- **No se incluye en el repositorio.** El archivo contiene el RUT de los titulares (columna `RUT_ROL`), por lo que `data/raw/` está en el `.gitignore`. Cada integrante lo descarga y lo deja en su computador.
- **Cómo obtenerlo:** descargar el CSV desde https://datos.gob.cl/dataset/tb-patentes-aguas y guardarlo, sin abrirlo ni modificarlo, como `data/raw/tb_patentes_aguas_december_2025_data.csv` (crear la carpeta `data/raw/` en la raíz del proyecto si no existe).
- **Integridad:** el archivo de `data/raw/` no se modifica nunca. Su hash SHA-256 permite verificar que es exactamente el mismo que usa el grupo:

      sha256sum data/raw/tb_patentes_aguas_december_2025_data.csv                  # Git Bash, Linux
      shasum -a 256 data/raw/tb_patentes_aguas_december_2025_data.csv              # macOS
      certutil -hashfile data\raw\tb_patentes_aguas_december_2025_data.csv SHA256  # Windows, cmd o PowerShell
      # SHA-256 esperado: f62e813e539172912c81adb73fb46a61040e793aeb30de7a764eae8b04064a30

## Estructura del repositorio

    proyecto-grupo9-mcdi500/
    ├─ data/
    │  ├─ raw/         datos originales, sin modificar (NO se suben: contienen RUT)
    │  └─ processed/   datos tras limpieza y transformación (F2)
    ├─ docs/           diccionario, fichas y documentación generada
    ├─ src/            módulos reutilizables (utilidades.py)
    ├─ F1/   Definición del problema y entorno reproducible
    │  ├─ F1_Definicion.ipynb    notebook de la fase
    │  └─ F1_Definicion.html     versión ejecutada, con salidas
    ├─ F2/   Obtención, limpieza y transformación de datos
    ├─ F3/   Núcleo algorítmico: programación estructurada, recursiva y POO
    ├─ F4/   Análisis, visualización y comunicación de resultados
    ├─ requirements.txt
    ├─ .gitignore
    └─ README.md

Los datos, `src/` y `docs/` son comunes a todas las fases; solo los notebooks e informes se separan por fase. Cada notebook localiza la raíz del proyecto por sí mismo, por lo que no usa rutas propias de ningún computador.

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

**4. Dejar el CSV en `data/raw/`** (ver la sección *Datos*) y verificar su hash SHA-256.

**5. Abrir JupyterLab desde la raíz del proyecto**

    python -m jupyterlab

En cada notebook, elegir el kernel **Python (grupo9-mcdi500)** y ejecutar con *Kernel → Restart Kernel and Run All Cells*, en orden (F1 → F4). Como `nbstripout` guarda los notebooks sin salidas, cada fase incluye además su versión ejecutada en HTML, que se genera con:

    python -m nbconvert --to html F1/F1_Definicion.ipynb

> Nota para Windows: si un comando como `nbstripout` o `jupyter kernelspec` responde *Permission denied* o *Acceso denegado*, ejecútelo como módulo de Python (`python -m nbstripout`, `python -m jupyterlab`).

## Fase 4: cómo reproducir el análisis

Desde la raíz del proyecto y con el entorno activo (no requiere el CSV original, solo `data/processed/`):

    python -m pytest -q                                   # 39 pruebas pasan, 1 se omite sin el CSV original
    python F4/generar_figuras.py                          # F4/figuras/fig1, fig2 y fig3
    python F4/generar_diagrama.py                         # docs/arquitectura.png
    python -m jupyter nbconvert --to notebook --execute --inplace F4/notebook_f4.ipynb
    python -m jupyter nbconvert --to html F4/notebook_f4.ipynb

El notebook `F4/notebook_f4.ipynb` regenera `F3/mediciones.md`, así que el informe, el HTML y el video usan las mismas cifras. El registro de cambios está en `changelog.md`.

> No vuelva a ejecutar la celda 3.2 del notebook F1: reescribiría `requirements.txt` sin las versiones fijas de las herramientas de Jupyter.

## Convención de commits

Prefijos del curso, con la descripción en presente y **sin tildes ni caracteres especiales**:

| Prefijo | Uso | Ejemplo |
|---|---|---|
| `docs` | Documentación, README, informe | `docs: documenta criterios de limpieza en el README` |
| `data` | Cambios en el procesamiento de los datos | `data: guarda tabla limpia en data/processed` |
| `feat` | Funcionalidad o análisis nuevo | `feat: notebook F1 con perfilamiento de nulos` |
| `fix` | Corrección de un error | `fix: corrige lectura de montos con separador de miles` |

Ramas por fase y tema (por ejemplo, `f2-limpieza-datos`), integradas a `main` mediante Pull Request revisado por otro integrante.

**Flujo diario:** `git pull` antes de empezar → trabajar → `git status` → `git add <archivo>` → `git commit -m "..."` → `git push`.

## Decisiones técnicas

- **Datos originales inmutables.** El CSV de `data/raw/` no se edita. Toda limpieza se programa en los notebooks y sus resultados se guardan en `data/processed/`, para que cualquier transformación pueda verificarse contra el original.
- **Registros incompletos conservados.** Los 691 registros sin año de patente y las filas con tesorería no identificada se mantienen en `data/raw/`. El criterio para tratarlos (imputar o excluir) se documentará en el notebook de F2, con su motivo e impacto.
- **Datos personales fuera del repositorio.** El CSV original contiene el RUT de los titulares, por lo que no se versiona: `data/raw/` está en el `.gitignore` y cada integrante lo descarga desde la fuente oficial, verificando el hash SHA-256. Por la misma razón, ningún archivo de `data/processed/` que conserve la columna `RUT_ROL` se sube al repositorio, y las salidas de los notebooks no muestran RUT.
- **Estructura común de datos.** Siguiendo la indicación del docente, los datos van en `data/` en la raíz (comunes a todas las fases) y no dentro de cada fase.
- **Notebooks sin salidas en Git.** `nbstripout` elimina las salidas antes de cada commit, para evitar diffs ilegibles y conflictos. Antes de entregar, cada notebook debe correr completo con *Restart Kernel and Run All Cells*.
- **`.gitignore` para equipos mixtos.** Excluye el entorno virtual, cachés, checkpoints de Jupyter, archivos de sistema de Windows y macOS, archivos de bloqueo de LibreOffice y Excel, y los datos originales (`data/raw/`). El notebook F1 lo regenera con este mismo contenido.
- **Dependencias directas.** `requirements.txt` lo genera el notebook F1 con las librerías que el proyecto importa (con su versión) y las herramientas del flujo de trabajo, sin dependencias transitivas, para que se instale igual en Windows y macOS.

## Uso de inteligencia artificial

El equipo utilizó herramientas de IA generativa (Anthropic, 2026) como apoyo en la documentación, en la configuración del entorno, en la Fase 4 en la redacción de borradores de `src/indicadores.py`, sus pruebas, `F4/` y el informe, y, en la Fase 3, en la orientación del trabajo con Git y GitHub y en la redacción de borradores del código de apoyo (`src/medicion.py`, `src/recursion.py` y `tests/`) y de la documentación de `F3/`. Cada integrante ejecutó el código en su equipo, los cambios se revisaron y aprobaron mediante pull requests, y las decisiones metodológicas, la verificación de resultados y el código entregado son responsabilidad de los integrantes, quienes pueden explicar cada paso del proyecto.
