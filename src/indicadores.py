"""Indicadores de morosidad con incertidumbre (Fase 4).

Funciones puras: reciben un DataFrame y devuelven uno nuevo, sin modificar el original.
  - intervalo_wilson: intervalo de confianza de Wilson para una proporción.
  - tasa_con_intervalo: tasa de morosidad, n de cobros e intervalo por grupo.
  - cargar_base_f4: une entrenamiento y prueba y reconstruye las categorías legibles.
"""
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
PROCESADOS = RAIZ / "data" / "processed"


def intervalo_wilson(exitos, n, z=1.96):
    """Intervalo de Wilson (95 % por defecto) para una proporción de `exitos` en `n` casos.

    Acepta escalares o arreglos. Con n = 0 devuelve (nan, nan).
    """
    exitos = np.asarray(exitos, dtype=float)
    n = np.asarray(n, dtype=float)
    if np.any(exitos < 0) or np.any(exitos > n):
        raise ValueError("Los éxitos deben estar entre 0 y n.")
    with np.errstate(divide="ignore", invalid="ignore"):
        p = exitos / n
        denom = 1 + z**2 / n
        centro = (p + z**2 / (2 * n)) / denom
        margen = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    inf = np.where(n == 0, np.nan, centro - margen)
    sup = np.where(n == 0, np.nan, centro + margen)
    if inf.ndim == 0:
        return float(inf), float(sup)
    return inf, sup


def tasa_con_intervalo(df, por, objetivo="moroso", z=1.96):
    """Tasa de morosidad por grupo con n de cobros e intervalo de Wilson.

    Devuelve un DataFrame con: el grupo, n, morosos, tasa, inf y sup.
    """
    for col in (por, objetivo):
        if col not in df.columns:
            raise KeyError(f"Falta la columna '{col}'.")
    g = df.groupby(por)[objetivo].agg(n="size", morosos="sum").reset_index()
    g["tasa"] = g["morosos"] / g["n"]
    g["inf"], g["sup"] = intervalo_wilson(g["morosos"].to_numpy(), g["n"].to_numpy(), z)
    return g


def cargar_base_f4():
    """Une entrenamiento y prueba (46.433 filas) y agrega `tesoreria` y `persona`."""
    df = pd.concat(
        [pd.read_csv(PROCESADOS / "entrenamiento_f3.csv"),
         pd.read_csv(PROCESADOS / "prueba_f3.csv")],
        ignore_index=True,
    )
    cols = [c for c in df.columns if c.startswith("teso_")]
    df["tesoreria"] = df[cols].idxmax(axis=1).str.replace("teso_", "", regex=False)
    df["persona"] = np.where(df["persona_juridica"] == 1, "jurídica", "natural")
    return df
