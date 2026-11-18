"""Pruebas de la clase base, las estrategias y los transformadores (II.c)."""
import numpy as np
import pandas as pd
import pytest

from transformadores import (CodificadorOneHot, CreacionMoroso, DejarNulo,
                             MedianaPorTesoreria, RellenarConValor,
                             TransformacionLog, Transformador, TratamientoAnio)


# ---------------- Casos normales ----------------
def test_creacion_moroso_normal(df_limpio):
    out = CreacionMoroso().ajustar_transformar(df_limpio)
    assert out["moroso"].tolist() == [1, 0, 0, 1, 0, 1]      # SALDO > 0


def test_log_normal_y_piso_en_cero(df_limpio):
    out = TransformacionLog().ajustar_transformar(df_limpio)
    assert out.loc[2, "LOG_SALDO"] == 0                       # saldo negativo -> 0
    assert out.loc[0, "LOG_MONTO"] == pytest.approx(np.log1p(1000.0))


def test_tratamiento_anio_rellena_y_marca(df_limpio):
    out = TratamientoAnio().ajustar_transformar(df_limpio)
    assert out["anio_faltante"].tolist() == [0, 1, 0, 0, 1, 0]
    assert out["ANIO_PATENTE"].tolist() == [2021, 0, 2023, 2022, 0, 2024]


def test_onehot_esquema_fijo_y_columna_original_se_elimina(df_limpio):
    cod = CodificadorOneHot("TIPO_PERSONA", prefijo="persona")
    out = cod.ajustar_transformar(df_limpio)
    assert "TIPO_PERSONA" not in out.columns
    assert out["persona_natural"].tolist() == [1, 0, 1, 0, 1, 1]
    assert (out["persona_natural"] + out["persona_juridica"] == 1).all()


def test_no_modifica_el_dataframe_original(df_limpio):
    copia = df_limpio.copy()
    TratamientoAnio().ajustar_transformar(df_limpio)
    TransformacionLog().ajustar_transformar(df_limpio)
    CreacionMoroso().ajustar_transformar(df_limpio)
    pd.testing.assert_frame_equal(df_limpio, copia)


# ---------------- Herencia, polimorfismo y encapsulamiento ----------------
def test_todos_son_transformadores(df_limpio):
    pasos = [TratamientoAnio(), CodificadorOneHot("TIPO_PERSONA", prefijo="persona"),
             TransformacionLog(), CreacionMoroso()]
    assert all(isinstance(p, Transformador) for p in pasos)


def test_clase_base_es_abstracta():
    with pytest.raises(TypeError):
        Transformador()


def test_parametros_devuelve_copia(df_limpio):
    cod = CodificadorOneHot("TIPO_PERSONA", prefijo="persona").ajustar(df_limpio)
    p = cod.parametros
    p["categorias"].clear()                                   # alterar la copia...
    assert cod.parametros["categorias"] != []                 # ...no cambia el estado


# ---------------- Excepciones ----------------
def test_transformar_antes_de_ajustar(df_limpio):
    with pytest.raises(RuntimeError):
        CreacionMoroso().transformar(df_limpio)


def test_columna_faltante(df_limpio):
    with pytest.raises(KeyError):
        CreacionMoroso().ajustar(df_limpio.drop(columns=["SALDO"]))


def test_tipo_equivocado_no_dataframe():
    with pytest.raises(TypeError):
        CreacionMoroso().ajustar([1, 2, 3])


def test_columna_no_numerica(df_limpio):
    df_limpio["SALDO"] = df_limpio["SALDO"].astype(str)
    with pytest.raises(TypeError):
        CreacionMoroso().ajustar(df_limpio)


def test_categoria_desconocida_al_ajustar(df_limpio):
    cod = CodificadorOneHot("TIPO_PERSONA", nombres={"NATURAL": "persona_natural"})
    with pytest.raises(ValueError, match="JURIDICA"):
        cod.ajustar(df_limpio)


def test_ajustar_con_cero_filas(df_limpio):
    with pytest.raises(ValueError):
        CreacionMoroso().ajustar(df_limpio.iloc[0:0])


# ---------------- Casos límite ----------------
def test_dataframe_de_una_fila(df_limpio):
    una = df_limpio.iloc[[0]]
    out = TratamientoAnio().ajustar_transformar(una)
    assert len(out) == 1 and out["anio_faltante"].iloc[0] == 0


def test_categoria_nueva_en_transformar_queda_en_ceros(df_limpio):
    cod = CodificadorOneHot("TIPO_PERSONA", nombres={"NATURAL": "persona_natural",
                                                      "JURIDICA": "persona_juridica"}).ajustar(df_limpio)
    nuevo = df_limpio.iloc[[0]].copy()
    nuevo["TIPO_PERSONA"] = "OTRA"
    out = cod.transformar(nuevo)
    assert out[["persona_natural", "persona_juridica"]].iloc[0].tolist() == [0, 0]


def test_saldo_exactamente_cero_no_es_moroso():
    df = pd.DataFrame({"SALDO": [0.0, 0.01, -1.0]})
    assert CreacionMoroso().ajustar_transformar(df)["moroso"].tolist() == [0, 1, 0]


# ---------------- Las tres estrategias del año faltante ----------------
def test_estrategia_rellenar_con_valor(df_limpio):
    out = TratamientoAnio(estrategia=RellenarConValor(0)).ajustar_transformar(df_limpio)
    assert out["ANIO_PATENTE"].isna().sum() == 0 and out.loc[1, "ANIO_PATENTE"] == 0


def test_estrategia_dejar_nulo(df_limpio):
    out = TratamientoAnio(estrategia=DejarNulo()).ajustar_transformar(df_limpio)
    assert out["ANIO_PATENTE"].isna().sum() == 2
    assert out["anio_faltante"].sum() == 2


def test_estrategia_mediana_por_tesoreria(df_limpio):
    out = TratamientoAnio(estrategia=MedianaPorTesoreria()).ajustar_transformar(df_limpio)
    assert out["ANIO_PATENTE"].isna().sum() == 0
    # fila 1 es ATACAMA, que solo tiene años faltantes -> mediana global (2022)
    assert out.loc[1, "ANIO_PATENTE"] == 2022