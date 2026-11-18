"""Pipeline que encadena transformadores (MCDI500, Grupo 9)."""

from transformadores import (CodificadorOneHot, CreacionMoroso, TransformacionLog,
                             Transformador, TratamientoAnio)

# Categoría original -> columna one-hot, en el orden de F2 (tabla de la sección 4a del
# notebook F2). Un diccionario fija el esquema: siempre salen las 18 columnas.
NOMBRES_TESORERIA = {
    "TESORERÍA REGIONAL DE ANTOFAGASTA": "teso_antofagasta",
    "TESORERÍA REGIONAL DE ARICA Y PARINACOTA": "teso_arica_parinacota",
    "TESORERÍA REGIONAL DE ATACAMA": "teso_atacama",
    "TESORERÍA REGIONAL DE AYSEN": "teso_aysen",
    "TESORERÍA REGIONAL DE COQUIMBO": "teso_coquimbo",
    "TESORERÍA REGIONAL DE LA ARAUCANIA": "teso_araucania",
    "TESORERÍA REGIONAL DE LOS LAGOS": "teso_los_lagos",
    "TESORERÍA REGIONAL DE LOS RIOS": "teso_los_rios",
    "TESORERÍA REGIONAL DE MAGALLANES": "teso_magallanes",
    "TESORERÍA REGIONAL DE TARAPACA": "teso_tarapaca",
    "TESORERÍA REGIONAL DE VALPARAÍSO": "teso_valparaiso",
    "TESORERÍA REGIONAL DE ÑUBLE": "teso_nuble",
    "TESORERÍA REGIONAL DEL BIO BIO": "teso_biobio",
    "TESORERÍA REGIONAL DEL MAULE": "teso_maule",
    "TESORERÍA REGIONAL LIB. GRAL BERNARDO OHIGGINS": "teso_ohiggins",
    "TESORERÍA REGIONAL SANTIAGO ORIENTE": "teso_santiago_oriente",
    "TESORERÍA REGIONAL SANTIAGO PONIENTE": "teso_santiago_poniente",
    "TESORERÍA REGIONAL SANTIAGO SUR": "teso_santiago_sur",
}


class Pipeline:
    """Ejecuta una lista de Transformador en orden, con la misma llamada para todos.

    No conoce a cada transformador: solo usa `ajustar_transformar` y `transformar`
    (polimorfismo), así que agregar o cambiar un paso no obliga a tocar el pipeline.
    """

    def __init__(self, pasos):
        pasos = list(pasos)
        if not pasos:
            raise ValueError("El pipeline necesita al menos un paso.")
        for paso in pasos:
            if not isinstance(paso, Transformador):
                raise TypeError(f"{paso!r} no es un Transformador.")
        self._pasos = pasos

    @property
    def pasos(self):
        return list(self._pasos)

    def ajustar_transformar(self, df):
        """Ajusta cada paso con el resultado del anterior (solo con entrenamiento)."""
        for paso in self._pasos:
            df = paso.ajustar_transformar(df)
        return df

    def transformar(self, df):
        """Aplica los pasos ya ajustados a datos nuevos (prueba), sin reajustar."""
        for paso in self._pasos:
            df = paso.transformar(df)
        return df

    def parametros(self):
        """Lo aprendido por cada paso, para guardarlo y reutilizarlo en F4."""
        return {f"{i}_{type(p).__name__}": p.parametros for i, p in enumerate(self._pasos, 1)}


def crear_pipeline_f2(estrategia_anio=None):
    """Pipeline que reproduce el procesamiento de F2, en el mismo orden."""
    return Pipeline([
        TratamientoAnio(estrategia=estrategia_anio),
        CodificadorOneHot("TESORERIA_REGIONAL", NOMBRES_TESORERIA),
        CodificadorOneHot("TIPO_PERSONA", prefijo="persona"),
        TransformacionLog(),
        CreacionMoroso(),
    ])
