"""Pruebas de src/indicadores.py: casos normales, límite y de excepción."""
import numpy as np
import pandas as pd
import pytest

from indicadores import intervalo_wilson, tasa_con_intervalo


def test_wilson_caso_conocido():
    inf, sup = intervalo_wilson(8, 10)
    assert inf == pytest.approx(0.4902, abs=1e-3)
    assert sup == pytest.approx(0.9433, abs=1e-3)


def test_wilson_contiene_la_proporcion():
    inf, sup = intervalo_wilson(np.array([3, 50, 90]), np.array([10, 100, 100]))
    p = np.array([0.3, 0.5, 0.9])
    assert np.all(inf < p) and np.all(p < sup)


def test_wilson_extremos_no_salen_de_0_y_1():
    inf0, sup0 = intervalo_wilson(0, 20)
    inf1, sup1 = intervalo_wilson(20, 20)
    assert inf0 == pytest.approx(0.0, abs=1e-12) and 0 < sup0 < 1
    assert 0 < inf1 < 1 and sup1 == pytest.approx(1.0, abs=1e-12)


def test_wilson_n_cero_devuelve_nan():
    inf, sup = intervalo_wilson(0, 0)
    assert np.isnan(inf) and np.isnan(sup)


def test_wilson_exitos_mayores_que_n_falla():
    with pytest.raises(ValueError):
        intervalo_wilson(11, 10)


def test_tasa_con_intervalo_por_grupo():
    df = pd.DataFrame({"g": ["a", "a", "a", "b", "b"], "moroso": [1, 1, 0, 0, 0]})
    out = tasa_con_intervalo(df, "g")
    assert out.loc[out.g == "a", "tasa"].iloc[0] == pytest.approx(2 / 3)
    assert out.loc[out.g == "b", "n"].iloc[0] == 2
    assert (out["inf"] <= out["tasa"]).all() and (out["tasa"] <= out["sup"]).all()


def test_tasa_con_intervalo_no_modifica_el_original():
    df = pd.DataFrame({"g": ["a", "b"], "moroso": [1, 0]})
    copia = df.copy()
    tasa_con_intervalo(df, "g")
    pd.testing.assert_frame_equal(df, copia)


def test_tasa_con_intervalo_columna_faltante():
    with pytest.raises(KeyError):
        tasa_con_intervalo(pd.DataFrame({"moroso": [1]}), "g")
