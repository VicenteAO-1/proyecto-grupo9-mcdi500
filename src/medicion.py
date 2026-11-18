"""Mediciones de tiempo y memoria (Fase 3, II.d).


Dos comparaciones sobre las 46.433 filas procesadas:
  1) calcular moroso con un bucle fila a fila vs. la versión vectorizada;
  2) calcular la tasa de morosidad por tesorería con un diccionario
     recorrido a mano vs. groupby.


Para cada versión: tiempo con timeit (se repite y se conserva el MENOR),
memoria máxima con tracemalloc y comprobación de que ambas dan lo mismo.
Ejecutar desde la raíz del proyecto:  python src/medicion.py
"""
import timeit
import tracemalloc
from pathlib import Path


import numpy as np
import pandas as pd


RAIZ = Path(__file__).resolve().parents[1]
PROCESADOS = RAIZ / "data" / "processed"




def cargar_base():
    """Une entrenamiento y prueba (46.433 filas) y reconstruye la tesorería."""
    df = pd.concat(
        [pd.read_csv(PROCESADOS / "entrenamiento_f3.csv"),
         pd.read_csv(PROCESADOS / "prueba_f3.csv")],
        ignore_index=True,
    )
    cols = [c for c in df.columns if c.startswith("teso_")]
    df["tesoreria"] = df[cols].idxmax(axis=1)
    return df[["SALDO", "tesoreria"]].copy()




# ---------- Comparación 1: variable moroso ----------
def moroso_bucle(df):
    """O(n) en Python puro: recorre fila a fila."""
    salida = []
    for saldo in df["SALDO"]:
        salida.append(1 if saldo > 0 else 0)
    return pd.Series(salida, index=df.index)




def moroso_vectorizado(df):
    """O(n) pero el recorrido ocurre en C (NumPy)."""
    return (df["SALDO"] > 0).astype(int)




# ---------- Comparación 2: tasa por tesorería ----------
def tasa_diccionario(df):
    """O(n) con un diccionario recorrido a mano: {tesorería: [morosos, total]}."""
    acum = {}
    for teso, saldo in zip(df["tesoreria"], df["SALDO"]):
        par = acum.setdefault(teso, [0, 0])
        par[0] += 1 if saldo > 0 else 0
        par[1] += 1
    return pd.Series({t: m / n for t, (m, n) in acum.items()}).sort_index()




def tasa_groupby(df):
    """O(n) con groupby (agrupación vectorizada en C)."""
    return (df["SALDO"] > 0).groupby(df["tesoreria"]).mean().sort_index()




# ---------- Utilidades de medición ----------
def medir_tiempo(funcion, df, repeticiones=7, numero=5):
    """Menor tiempo por llamada (s) entre varias repeticiones."""
    t = timeit.repeat(lambda: funcion(df), repeat=repeticiones, number=numero)
    return min(t) / numero




def medir_memoria(funcion, df):
    """Pico de memoria (MiB) asignada durante una llamada."""
    tracemalloc.start()
    funcion(df)
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return pico / 1024 ** 2




def comparar(nombre, f_lenta, f_rapida, df, igual):
    """Mide ambas versiones y devuelve filas para la tabla."""
    r1, r2 = f_lenta(df), f_rapida(df)
    assert igual(r1, r2), f"{nombre}: las versiones NO dan el mismo resultado"
    filas = []
    for etiqueta, f in ((f_lenta.__name__, f_lenta), (f_rapida.__name__, f_rapida)):
        filas.append({
            "comparación": nombre,
            "versión": etiqueta,
            "tiempo_s": medir_tiempo(f, df),
            "memoria_MiB": medir_memoria(f, df),
        })
    t1, t2 = filas[0]["tiempo_s"], filas[1]["tiempo_s"]
    print(f"{nombre}: mismo resultado = True; la versión rápida es {t1 / t2:.1f} veces más veloz")
    return filas




def main():
    df = cargar_base()
    print(f"Filas medidas: {len(df):,}".replace(",", "."))
    filas = []
    filas += comparar("moroso", moroso_bucle, moroso_vectorizado, df,
                      lambda a, b: np.array_equal(a.to_numpy(), b.to_numpy()))
    filas += comparar("tasa por tesorería", tasa_diccionario, tasa_groupby, df,
                      lambda a, b: np.allclose(a.to_numpy(), b.to_numpy())
                      and list(a.index) == list(b.index))
    tabla = pd.DataFrame(filas)
    print(tabla.to_string(index=False, float_format=lambda x: f"{x:.6f}"))
    return tabla




if __name__ == "__main__":
    main()
