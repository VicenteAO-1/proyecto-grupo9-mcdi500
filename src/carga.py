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


# ----------------------------------------------------------------------------
# Salidas de F3 para F4: diccionario de columnas y guardado de entregables
# ----------------------------------------------------------------------------
DESCRIPCIONES = {
    "MONTO": "Monto asociado a la patente",
    "SALDO": "Saldo impago de la patente (negativo = pago en exceso)",
    "PAGADO": "Monto pagado",
    "ANIO_PATENTE": "Año de la patente (0 = faltante en el archivo)",
    "UTM": "Valor registrado en UTM",
    "anio_faltante": "1 si el año de la patente no venía en el archivo",
    "moroso": "Variable objetivo: 1 si SALDO > 0, 0 en otro caso",
}


def describir_columnas(df, originales, objetivo="moroso", excluidas=()):
    """Devuelve un DataFrame con el diccionario del conjunto procesado.

    Parámetros
    ----------
    df : pd.DataFrame
        Conjunto ya procesado.
    originales : iterable de str
        Columnas que vienen del archivo original (para marcar el origen).
    objetivo : str
        Nombre de la variable objetivo.
    excluidas : iterable de str
        Columnas que no deben entrar al modelado (por ejemplo, por fuga de información).

    Retorna
    -------
    pd.DataFrame
        Una fila por columna: tipo, rol, origen, nulos y descripción.
    """
    originales, excluidas = set(originales), set(excluidas)
    filas = []
    for col in df.columns:
        if col == objetivo:
            rol, origen = "objetivo", "derivada de SALDO"
        else:
            rol = "excluida del modelado" if col in excluidas else "predictora"
            if col in originales:
                origen = "original"
            elif col.startswith("LOG_"):
                origen = f"log1p de {col[4:]}"
            elif col.startswith("teso_"):
                origen = "one-hot de TESORERIA_REGIONAL"
            elif col.startswith("persona_"):
                origen = "one-hot de TIPO_PERSONA"
            elif col == "anio_faltante":
                origen = "indicador de ANIO_PATENTE"
            else:
                origen = "derivada"
        if col in DESCRIPCIONES:
            desc = DESCRIPCIONES[col]
        elif col.startswith("LOG_"):
            desc = f"Logaritmo log1p de {col[4:]} (valores negativos pasan a 0)"
        elif col.startswith(("teso_", "persona_")):
            desc = "Indicador binario (1 = la fila pertenece a esta categoría)"
        else:
            desc = ""
        filas.append({"columna": col, "tipo": str(df[col].dtype), "rol": rol,
                      "origen": origen, "nulos": int(df[col].isna().sum()),
                      "descripcion": desc})
    return pd.DataFrame(filas)


def guardar_entregables(entrenamiento, prueba, pipeline, diccionario, carpeta):
    """Guarda en `carpeta` los cuatro archivos que recibe F4.

    Escribe entrenamiento_f3.csv, prueba_f3.csv, diccionario_f3.csv y
    parametros_f3.csv (lo que aprendió cada paso del pipeline, en JSON).
    Retorna un dict {nombre: ruta}.
    """
    import json

    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    rutas = {
        "entrenamiento": carpeta / "entrenamiento_f3.csv",
        "prueba": carpeta / "prueba_f3.csv",
        "diccionario": carpeta / "diccionario_f3.csv",
        "parametros": carpeta / "parametros_f3.csv",
    }
    entrenamiento.to_csv(rutas["entrenamiento"], index=False)
    prueba.to_csv(rutas["prueba"], index=False)
    diccionario.to_csv(rutas["diccionario"], index=False)
    pd.DataFrame(
        [{"orden": i, "paso": nombre.split("_", 1)[1],
          "parametros": json.dumps(valores, ensure_ascii=False, default=str)}
         for i, (nombre, valores) in enumerate(pipeline.parametros().items(), start=1)]
    ).to_csv(rutas["parametros"], index=False)
    return rutas
