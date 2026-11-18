"""Configuración común de las pruebas: ruta de importación y datos de ejemplo."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))   # los módulos de src/ se importan sin el prefijo `src.`

TESORERIAS = ["TESORERÍA REGIONAL DE ANTOFAGASTA", "TESORERÍA REGIONAL DE ATACAMA",
              "TESORERÍA REGIONAL SANTIAGO SUR"]


@pytest.fixture
def df_limpio():
    """DataFrame pequeño con la estructura que sale de `preparar_crudo` (7 columnas)."""
    return pd.DataFrame({
        "TIPO_PERSONA": ["NATURAL", "JURIDICA", "NATURAL", "JURIDICA", "NATURAL", "NATURAL"],
        "MONTO": [1000.0, 5000.0, 250.0, 80000.0, 1200.0, 300.0],
        "SALDO": [1000.0, 0.0, -50.0, 80000.0, 0.0, 300.0],
        "PAGADO": [0.0, 5000.0, 300.0, 0.0, 1200.0, 0.0],
        "TESORERIA_REGIONAL": [TESORERIAS[0], TESORERIAS[1], TESORERIAS[2],
                               TESORERIAS[0], TESORERIAS[1], TESORERIAS[2]],
        "ANIO_PATENTE": [2021.0, np.nan, 2023.0, 2022.0, np.nan, 2024.0],
        "UTM": [50000.0, 62000.0, 64000.0, 61000.0, 60000.0, 65000.0],
    })