"""Pruebas del Pipeline, de la carga y de la comparación con F2 (II.c)."""
from pathlib import Path

import pandas as pd
import pytest

from carga import (cargar_datos, eliminar_columnas, eliminar_filas_nulas,
                   preparar_crudo)
from pipeline import Pipeline, crear_pipeline_f2
from transformadores import CreacionMoroso, TransformacionLog

RAIZ = Path(__file__).resolve().parents[1]


# ---------------- Pipeline ----------------
def test_pipeline_completo_columnas(df_limpio):
    out = crear_pipeline_f2().ajustar_transformar(df_limpio)
    assert len(out) == len(df_limpio)
    assert out.shape[1] == 31                       # 31 columnas, igual que F2
    assert "TESORERIA_REGIONAL" not in out.columns
    assert out["moroso"].tolist() == [1, 0, 0, 1, 0, 1]
    assert out.isna().sum().sum() == 0


def test_pipeline_transformar_usa_lo_aprendido_en_entrenamiento(df_limpio):
    pipe = crear_pipeline_f2()
    entrenamiento = pipe.ajustar_transformar(df_limpio.iloc[:4])
    prueba = pipe.transformar(df_limpio.iloc[4:])
    assert list(prueba.columns) == list(entrenamiento.columns)   # mismo esquema


def test_pipeline_no_modifica_entrada(df_limpio):
    copia = df_limpio.copy()
    crear_pipeline_f2().ajustar_transformar(df_limpio)
    pd.testing.assert_frame_equal(df_limpio, copia)


def test_pipeline_parametros_un_dict_por_paso():
    p = crear_pipeline_f2().parametros()
    assert len(p) == 5 and list(p)[0].startswith("1_TratamientoAnio")


def test_pipeline_sin_pasos():
    with pytest.raises(ValueError):
        Pipeline([])


def test_pipeline_paso_que_no_es_transformador():
    with pytest.raises(TypeError):
        Pipeline([CreacionMoroso(), "no soy un transformador"])


def test_pipeline_es_polimorfico(df_limpio):
    out = Pipeline([TransformacionLog(), CreacionMoroso()]).ajustar_transformar(df_limpio)
    assert {"LOG_MONTO", "moroso"} <= set(out.columns)


# ---------------- Carga y limpieza ----------------
def test_cargar_archivo_inexistente(tmp_path):
    with pytest.raises(FileNotFoundError, match="data/raw"):
        cargar_datos(tmp_path / "no_existe.csv")


def test_eliminar_filas_nulas_no_modifica_original(df_limpio):
    df = df_limpio.copy()
    df.loc[0, "TESORERIA_REGIONAL"] = None
    copia = df.copy()
    out = eliminar_filas_nulas(df, "TESORERIA_REGIONAL")
    assert len(out) == len(df) - 1
    pd.testing.assert_frame_equal(df, copia)


def test_eliminar_filas_nulas_columna_inexistente(df_limpio):
    with pytest.raises(KeyError):
        eliminar_filas_nulas(df_limpio, "NO_EXISTE")


def test_eliminar_columnas_ausentes(df_limpio):
    with pytest.raises(KeyError):
        eliminar_columnas(df_limpio)    # no trae las columnas que F2 descarta


# ---------------- Comparación con F2 (solo si el archivo crudo está en el equipo) ----------------
RAW = RAIZ / "data" / "raw" / "tb_patentes_aguas_december_2025_data.csv"
F2 = RAIZ / "data" / "processed" / "tb_patentes_aguas_december_2025_data.csv"


@pytest.mark.skipif(not (RAW.exists() and F2.exists()), reason="falta el archivo crudo o el de F2")
def test_pipeline_reproduce_f2():
    limpio = preparar_crudo(cargar_datos(RAW))
    out = crear_pipeline_f2().ajustar_transformar(limpio)
    esperado = pd.read_csv(F2)
    assert out.shape == esperado.shape == (46433, 31)
    pd.testing.assert_frame_equal(out[esperado.columns], esperado, check_dtype=False)