"""Carga de datos y pasos de limpieza funcionales del proyecto (MCDI500, Grupo 9).

Cada función recibe un DataFrame y devuelve uno NUEVO: nunca modifica el original.
"""

from pathlib import Path

import pandas as pd

# Columnas que F2 descarta antes de transformar (identificadores, fechas y
# variables de alta cardinalidad que no entran al análisis).
COLUMNAS_A_ELIMINAR = [
    "FECHA", "RUT_ROL", "RUT_ROL_DV", "CUENTA", "FORM_FOLIO", "MOV_TIPO",
    "FECHA_EJECUCION", "TESORERIA", "OFICINA", "OFICINA_CBR", "COMUNA",
    "PROVINCIA", "CONCESION", "N_DE_CORRELATIVO_O_PATENTE",
]


def cargar_datos(ruta):
    """Carga un CSV en un DataFrame.

    Parámetros
    ----------
    ruta : str o Path
        Ruta del archivo CSV.

    Retorna
    -------
    pd.DataFrame
        Datos tal como vienen en el archivo.

    Lanza
    -----
    FileNotFoundError
        Si el archivo no existe, con un mensaje que indica dónde debe estar.
    """
    ruta = Path(ruta)
    try:
        return pd.read_csv(ruta)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"No se encontró {ruta.name} en {ruta.parent.resolve()}. "
            "Debe estar en data/raw/ de la raíz del proyecto."
        ) from None


def eliminar_columnas(df, columnas=None):
    """Devuelve una copia sin las columnas indicadas (por defecto, las de F2).

    Lanza KeyError si alguna columna a eliminar no existe, para detectar a tiempo
    un archivo con otra estructura.
    """
    columnas = COLUMNAS_A_ELIMINAR if columnas is None else list(columnas)
    faltantes = [c for c in columnas if c not in df.columns]
    if faltantes:
        raise KeyError(f"Columnas ausentes en el DataFrame: {faltantes}")
    return df.drop(columns=columnas)


def eliminar_filas_nulas(df, columna):
    """Devuelve una copia sin las filas que tienen nulo en `columna`.

    El índice se reinicia, igual que en F2, para que el resultado sea comparable.
    """
    if columna not in df.columns:
        raise KeyError(f"La columna '{columna}' no existe en el DataFrame.")
    return df.dropna(subset=[columna]).reset_index(drop=True)


def preparar_crudo(df):
    """Aplica la limpieza de F2 previa a los transformadores.

    Quita las columnas descartadas y las filas sin TESORERIA_REGIONAL
    (34 filas en el archivo real: 46.467 -> 46.433).
    """
    return eliminar_filas_nulas(eliminar_columnas(df), "TESORERIA_REGIONAL")
