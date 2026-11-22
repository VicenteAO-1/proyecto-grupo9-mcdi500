"""Genera las tres figuras de la Fase 4 en F4/figuras/ (se llama desde notebook_f4.ipynb).

Cada título enuncia el hallazgo; las cifras del título se calculan desde los datos.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from indicadores import cargar_base_f4, tasa_con_intervalo

NAVY, RED, GR = "#1E395E", "#A9172B", "#6B7280"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False})
FUENTE = "Fuente: Tesorería General de la República, datos abiertos, corte a diciembre de 2025; elaboración propia."
SALIDA = RAIZ / "F4" / "figuras"
pct = lambda x, d=1: f"{x:.{d}f}".replace(".", ",")


def titulo(ax, texto):
    ax.set_title(texto, loc="left", fontweight="bold", fontsize=10)


TILDES = {"Araucania": "Araucanía", "Biobio": "Biobío", "Nuble": "Ñuble", "Aysen": "Aysén", "Los Rios": "Los Ríos",
          "Valparaiso": "Valparaíso", "Ohiggins": "O'Higgins", "Arica Parinacota": "Arica y Parinacota", "Tarapaca": "Tarapacá"}


def nombre(x):
    n = x.replace("_", " ").title()
    return TILDES.get(n, n)


df = cargar_base_f4()
glob = df.moroso.mean() * 100

# ---- Figura 1: tasa por año de patente (sin las filas sin año)
con = df[df.anio_faltante == 0]
a = tasa_con_intervalo(con, "ANIO_PATENTE")
antes = con[con.ANIO_PATENTE <= 2020].moroso.mean() * 100
despues = con[con.ANIO_PATENTE >= 2021].moroso.mean() * 100
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.fill_between(a.ANIO_PATENTE, a.inf * 100, a.sup * 100, color=NAVY, alpha=.2, label="Intervalo de Wilson 95 %")
ax.plot(a.ANIO_PATENTE, a.tasa * 100, color=NAVY, marker="o", ms=4, label="Tasa de morosidad")
ax.axvline(2020.5, color=RED, ls="--", lw=1)
ax.text(2020.4, 52, "Desde 2021", color=RED, ha="right", fontsize=9)
ax.set_xticks(range(2007, 2026, 2)); ax.set_ylim(50, 100)
ax.set_xlabel("Año de la patente"); ax.set_ylabel("Cobros con saldo impago (%)")
titulo(ax, f"La morosidad baja de {pct(antes,0)} % a {pct(despues,0)} % desde las patentes de 2021")
ax.legend(frameon=False, loc="lower left")
fig.text(.01, .01, FUENTE + " Excluye 691 cobros sin año.", fontsize=7, color=GR)
fig.tight_layout(rect=(0, .04, 1, 1)); fig.savefig(SALIDA / "fig1_tasa_por_anio.png", dpi=200); plt.close()

# ---- Figura 2: barras horizontales ordenadas por tesorería, con intervalo y referencia global
t = tasa_con_intervalo(df, "tesoreria").sort_values("tasa")
lab = [f"{nombre(x)} (n={n:,})".replace(",", ".") for x, n in zip(t.tesoreria, t.n)]
y = np.arange(len(t))
fig, ax = plt.subplots(figsize=(8, 5.8))
ax.barh(y, t.tasa * 100, color="#9FB3CF", edgecolor=NAVY, height=.7)
ax.errorbar(t.tasa * 100, y, xerr=[(t.tasa - t.inf) * 100, (t.sup - t.tasa) * 100], fmt="none", ecolor=NAVY, capsize=2, lw=1)
ax.axvline(glob, color=RED, ls="--", lw=1.2)
ax.text(glob + .8, 0, f"Total {pct(glob,2)} %", color=RED, fontsize=8.5)
ax.set_yticks(y); ax.set_yticklabels(lab, fontsize=8.5); ax.set_xlim(0, 100)
ax.set_xlabel("Cobros con saldo impago (%), con intervalo de Wilson 95 %")
titulo(ax, f"La morosidad va de {pct(t.tasa.min()*100,0)} % a {pct(t.tasa.max()*100,0)} % según la tesorería")
fig.text(.01, .01, FUENTE, fontsize=7, color=GR)
fig.tight_layout(rect=(0, .03, 1, 1)); fig.savefig(SALIDA / "fig2_tasa_por_tesoreria.png", dpi=200); plt.close()

# ---- Figura 3: distribución del monto en UTM (violín con caja interior, escala logarítmica)
u = [df[df.moroso == 0].UTM.clip(lower=.01), df[df.moroso == 1].UTM.clip(lower=.01)]
d = [np.log10(x) for x in u]              # el violín se calcula sobre log10 para que la escala sea logarítmica
fig, ax = plt.subplots(figsize=(8, 4.2))
vp = ax.violinplot(d, positions=[1, 2], orientation="horizontal", widths=.8, showextrema=False)
for cuerpo in vp["bodies"]:
    cuerpo.set(facecolor="#C9D3E3", edgecolor=NAVY, alpha=1)
bp = ax.boxplot(d, positions=[1, 2], orientation="horizontal", widths=.12, whis=(5, 95), showfliers=False,
                patch_artist=True, medianprops=dict(color=RED, lw=2), manage_ticks=False)
for b in bp["boxes"]:
    b.set(facecolor="white", edgecolor=NAVY)
ax.set_yticks([1, 2], ["Sin saldo impago", "Con saldo impago"])
ax.set_xticks(range(-2, 4), [f"10^{k}".replace("^", "") if False else f"{10.0 ** k:g}" for k in range(-2, 4)])
ax.set_xlabel("Monto de la patente (UTM, escala logarítmica)")
for i, x in enumerate(u, 1):
    ax.text(np.log10(x.median()) + .08, i + .3, f"Mediana: {pct(x.median(),1)} UTM", fontsize=8.5, color=RED)
titulo(ax, f"Los cobros con saldo impago tienen mayor monto mediano ({pct(u[1].median(),0)} frente a {pct(u[0].median(),0)} UTM)")
fig.text(.01, .01, FUENTE + " Violín: densidad; caja: rango intercuartílico y p5 a p95.", fontsize=7, color=GR)
fig.tight_layout(rect=(0, .04, 1, 1)); fig.savefig(SALIDA / "fig3_monto_por_situacion.png", dpi=200); plt.close()
