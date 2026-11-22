"""Genera el diagrama de arquitectura (docs/arquitectura.png) usado en el informe de la Fase 4."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

RAIZ = Path(__file__).resolve().parents[1]
NAVY, GRIS = "#1E395E", "#E8EDF5"
fig, ax = plt.subplots(figsize=(9, 3.6)); ax.set_xlim(0, 100); ax.set_ylim(0, 40); ax.axis("off")

def caja(x, y, w, h, texto, fc=GRIS, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.2", fc=fc, ec=NAVY, lw=1.2))
    ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center", fontsize=8, fontweight="bold" if bold else "normal")

def flecha(x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.2))

caja(1, 26, 17, 10, "data/processed/\nentrenamiento_f3.csv\nprueba_f3.csv")
caja(24, 26, 17, 10, "src/carga.py\ncarga y verifica")
caja(47, 26, 24, 10, "src/pipeline.py\nPipeline de\ntransformadores", bold=True)
caja(77, 26, 22, 10, "src/indicadores.py\nWilson y tasas\npor grupo")
for a, b in [(18.5, 24), (41.5, 47), (71.5, 77)]:
    flecha(a, 31, b, 31)
caja(43, 4, 32, 16, "Transformador (clase base abstracta)\n  TratamientoAnio  ← EstrategiaAnio\n  CodificadorOneHot\n  TransformacionLog\n  CreacionMoroso", fc="#FFFFFF")
flecha(59, 26, 59, 20.5)
caja(1, 6, 17, 10, "src/recursion.py\nsrc/medicion.py")
caja(24, 6, 17, 10, "tests/ (pytest)\n40 pruebas")
caja(77, 6, 22, 10, "F4/generar_figuras.py\nF4/notebook_f4.ipynb")
flecha(88, 26, 88, 16.5)
ax.text(50, 38.6, "Flujo de datos y módulos del proyecto", ha="center", fontsize=9.5, fontweight="bold")
fig.savefig(RAIZ / "docs" / "arquitectura.png", dpi=200, bbox_inches="tight"); plt.close()
