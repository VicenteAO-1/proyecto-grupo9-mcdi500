"""Clase base Transformador y los transformadores del pipeline (MCDI500, Grupo 9).

Patrón ajustar / transformar: lo que se aprende de los datos (categorías, medianas)
se calcula SOLO en `ajustar`, con el conjunto de entrenamiento, y `transformar`
lo reutiliza sin volver a mirar los datos nuevos.
"""

import copy
import re
import unicodedata
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd


class Transformador(ABC):
    """Clase base de todos los pasos del pipeline.

    Las subclases implementan `_aprender` y `_aplicar`; la validación, el control
    de estado y la copia del DataFrame viven aquí (encapsulamiento). El estado
    aprendido es privado: se consulta con la propiedad `parametros`.
    """

    def __init__(self):
        self.__estado = {}          # privado: solo `ajustar` lo escribe
        self.__ajustado = False

    # ---- API pública (la misma para todas las subclases: polimorfismo) ----
    def ajustar(self, df):
        """Aprende del DataFrame lo que el paso necesite. Devuelve self."""
        self._validar(df)
        if len(df) == 0:
            raise ValueError(f"{type(self).__name__}: no se puede ajustar con 0 filas.")
        self.__estado = dict(self._aprender(df) or {})
        self.__ajustado = True
        return self

    def transformar(self, df):
        """Devuelve un DataFrame NUEVO transformado; el original no se modifica."""
        if not self.__ajustado:
            raise RuntimeError(f"{type(self).__name__}: llame a ajustar() antes de transformar().")
        self._validar(df)
        return self._aplicar(df.copy(), copy.deepcopy(self.__estado))

    def ajustar_transformar(self, df):
        """Atajo: ajusta y transforma con el mismo DataFrame (solo entrenamiento)."""
        return self.ajustar(df).transformar(df)

    @property
    def ajustado(self):
        return self.__ajustado

    @property
    def parametros(self):
        """Copia de lo aprendido en `ajustar` (para guardarlo en parametros_f3)."""
        return copy.deepcopy(self.__estado)

    # ---- Contrato para las subclases ----
    @abstractmethod
    def _columnas_requeridas(self):
        """Lista de columnas que debe traer el DataFrame de entrada."""

    def _columnas_numericas(self):
        """Columnas que además deben ser numéricas (por defecto, ninguna)."""
        return []

    def _aprender(self, df):
        """Devuelve un dict con lo aprendido. Por defecto, nada."""
        return {}

    @abstractmethod
    def _aplicar(self, df, estado):
        """Recibe una copia del DataFrame y el estado aprendido; devuelve el resultado."""

    # ---- Validación común ----
    def _validar(self, df):
        nombre = type(self).__name__
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"{nombre}: se esperaba un DataFrame y se recibió {type(df).__name__}.")
        faltantes = [c for c in self._columnas_requeridas() if c not in df.columns]
        if faltantes:
            raise KeyError(f"{nombre}: faltan las columnas {faltantes}.")
        no_numericas = [c for c in self._columnas_numericas()
                        if not pd.api.types.is_numeric_dtype(df[c])]
        if no_numericas:
            raise TypeError(f"{nombre}: las columnas {no_numericas} deben ser numéricas.")


# ----------------------------------------------------------------------------
# Patrón Strategy: cómo se trata el año faltante. TratamientoAnio no cambia al
# elegir una u otra; solo recibe otra estrategia.
# ----------------------------------------------------------------------------
class EstrategiaAnio(ABC):
    """Interfaz de las estrategias para rellenar el año faltante."""

    def aprender(self, df, columna):
        """Devuelve un dict con lo que la estrategia aprende del entrenamiento."""
        return {}

    @abstractmethod
    def aplicar(self, df, columna, estado):
        """Devuelve la columna `columna` ya tratada (Series)."""


class RellenarConValor(EstrategiaAnio):
    """Rellena con un valor centinela (0 en F2) y deja la columna entera."""

    def __init__(self, valor=0):
        self.valor = valor

    def aplicar(self, df, columna, estado):
        return df[columna].fillna(self.valor).astype(int)


class DejarNulo(EstrategiaAnio):
    """No imputa: el año faltante queda como NaN (solo queda el indicador)."""

    def aplicar(self, df, columna, estado):
        return df[columna]


class MedianaPorTesoreria(EstrategiaAnio):
    """Imputa con la mediana del año por tesorería, aprendida en el entrenamiento."""

    def __init__(self, grupo="TESORERIA_REGIONAL"):
        self.grupo = grupo

    def aprender(self, df, columna):
        return {"mediana_global": float(df[columna].median()),
                "mediana_por_grupo": df.groupby(self.grupo)[columna].median().to_dict()}

    def aplicar(self, df, columna, estado):
        por_grupo = df[self.grupo].map(estado["mediana_por_grupo"])
        relleno = por_grupo.fillna(estado["mediana_global"])   # tesorería no vista
        return df[columna].fillna(relleno).round().astype(int)


class TratamientoAnio(Transformador):
    """Marca el año faltante con `anio_faltante` y lo trata según la estrategia.

    Con RellenarConValor(0) reproduce exactamente lo hecho en F2.
    """

    def __init__(self, columna="ANIO_PATENTE", indicador="anio_faltante", estrategia=None):
        super().__init__()
        self.columna = columna
        self.indicador = indicador
        self.estrategia = RellenarConValor(0) if estrategia is None else estrategia

    def _columnas_requeridas(self):
        extra = [getattr(self.estrategia, "grupo", None)]
        return [self.columna] + [c for c in extra if c]

    def _aprender(self, df):
        return self.estrategia.aprender(df, self.columna)

    def _aplicar(self, df, estado):
        # El indicador se crea ANTES del relleno, para no perder qué filas no tenían dato.
        df[self.indicador] = df[self.columna].isna().astype(int)
        df[self.columna] = self.estrategia.aplicar(df, self.columna, estado)
        return df


def _normalizar_texto(valor):
    """Texto en forma NFC y sin espacios sobrantes, para comparar categorías."""
    return unicodedata.normalize("NFC", str(valor)).strip()


def _nombre_columna(prefijo, categoria):
    """Nombre automático de columna: prefijo + categoría sin tildes ni símbolos."""
    base = unicodedata.normalize("NFKD", str(categoria)).encode("ascii", "ignore").decode()
    base = re.sub(r"[^a-z0-9]+", "_", base.lower()).strip("_")
    return f"{prefijo}_{base}"


class CodificadorOneHot(Transformador):
    """Codificación one-hot de una variable nominal.

    Dos modos:
    - `nombres` = dict {categoría: nombre_de_columna}: esquema FIJO. Las columnas
      salen siempre, en el orden del diccionario, aunque la categoría no aparezca
      en la muestra (sirve para una fila, para pruebas y para el archivo de 2026).
      Si los datos traen una categoría que no está en el dict, `ajustar` falla
      con un error que la nombra.
    - `nombres` = None: las categorías se aprenden en `ajustar` (orden alfabético)
      y se nombran con `prefijo` + categoría.
    En `transformar`, una categoría nueva queda en ceros, sin lanzar error.
    """

    def __init__(self, columna, nombres=None, prefijo=None):
        super().__init__()
        self.columna = columna
        self.nombres = None if nombres is None else {_normalizar_texto(k): v for k, v in nombres.items()}
        self.prefijo = prefijo or columna.lower()

    def _columnas_requeridas(self):
        return [self.columna]

    def _aprender(self, df):
        vistas = sorted({_normalizar_texto(v) for v in df[self.columna].dropna().unique()})
        if self.nombres is not None:
            desconocidas = [v for v in vistas if v not in self.nombres]
            if desconocidas:
                raise ValueError(
                    f"'{self.columna}' trae categorías que no están en el diccionario "
                    f"de nombres: {desconocidas}")
            return {"categorias": list(self.nombres), "nombres": list(self.nombres.values())}
        return {"categorias": vistas, "nombres": [_nombre_columna(self.prefijo, c) for c in vistas]}

    def _aplicar(self, df, estado):
        texto = df[self.columna].map(lambda v: v if pd.isna(v) else _normalizar_texto(v))
        nuevas = pd.DataFrame(
            {nom: (texto == cat).astype(int).to_numpy()
             for cat, nom in zip(estado["categorias"], estado["nombres"])},
            index=df.index)
        df = df.drop(columns=[self.columna]).reset_index(drop=True)
        return pd.concat([df, nuevas.reset_index(drop=True)], axis=1)


class TransformacionLog(Transformador):
    """Crea LOG_<col> = log1p(max(col, 0)) para cada columna indicada.

    Los saldos negativos (sobrepagos) pasan a 0 solo para calcular el logaritmo.
    No aprende nada de los datos, pero comparte la misma interfaz.
    """

    def __init__(self, columnas=("MONTO", "UTM", "SALDO", "PAGADO")):
        super().__init__()
        self.columnas = list(columnas)

    def _columnas_requeridas(self):
        return self.columnas

    def _columnas_numericas(self):
        return self.columnas

    def _aplicar(self, df, estado):
        for col in self.columnas:
            df[f"LOG_{col}"] = np.log1p(df[col].clip(lower=0))
        return df


class CreacionMoroso(Transformador):
    """Crea la variable objetivo: moroso = 1 si SALDO > 0, 0 en otro caso."""

    def __init__(self, columna="SALDO", objetivo="moroso"):
        super().__init__()
        self.columna = columna
        self.objetivo = objetivo

    def _columnas_requeridas(self):
        return [self.columna]

    def _columnas_numericas(self):
        return [self.columna]

    def _aplicar(self, df, estado):
        df[self.objetivo] = (df[self.columna] > 0).astype(int)
        return df
