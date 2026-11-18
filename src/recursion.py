
"""Recursión sobre los metadatos del proyecto (Fase 3, II.e).

Los metadatos (`docs/metadatos_proyecto.csv`) son pares clave-valor con claves
punteadas (`datos.fuente.autor`). Aquí se convierten en un diccionario anidado y
se recorren con funciones recursivas para detectar campos vacíos o pendientes
antes de guardar.

Caso base: el valor NO es un diccionario (es una hoja del árbol).
Caso recursivo: el valor es un diccionario, y se llama de nuevo a la función
sobre cada uno de sus hijos.
"""
from pathlib import Path

import pandas as pd

MARCAS_PENDIENTE = ("pendiente", "todo", "por definir", "tbd")


def anidar(plano):
    """Convierte {'datos.fuente.autor': 'x'} en {'datos': {'fuente': {'autor': 'x'}}}."""
    arbol = {}
    for clave, valor in plano.items():
        if not isinstance(clave, str) or not clave:
            raise ValueError(f"Clave inválida: {clave!r}")
        nodo = arbol
        *camino, hoja = clave.split(".")
        for parte in camino:
            nodo = nodo.setdefault(parte, {})
            if not isinstance(nodo, dict):
                raise ValueError(f"La clave '{clave}' choca con una hoja existente.")
        nodo[hoja] = valor
    return arbol


def es_vacio_o_pendiente(valor):
    """True si el valor es None, NaN, texto vacío o una marca de pendiente."""
    if valor is None:
        return True
    try:
        if pd.isna(valor):
            return True
    except (TypeError, ValueError):
        pass
    if isinstance(valor, str):
        texto = valor.strip().lower()
        return texto == "" or any(m in texto for m in MARCAS_PENDIENTE)
    return False


def buscar_pendientes(metadatos, ruta=""):
    """Devuelve la lista de rutas (con puntos) de los campos vacíos o pendientes.

    Recursiva: si un valor es un diccionario, se baja un nivel; si no, es la hoja
    (caso base) y se revisa. Un diccionario vacío también se informa como pendiente.
    """
    if not isinstance(metadatos, dict):                      # caso base: hoja
        return [ruta] if es_vacio_o_pendiente(metadatos) else []
    if not metadatos:                                        # rama sin contenido
        return [ruta] if ruta else []
    pendientes = []
    for clave, valor in metadatos.items():                   # caso recursivo
        sub = f"{ruta}.{clave}" if ruta else str(clave)
        pendientes.extend(buscar_pendientes(valor, sub))
    return pendientes


def contar_campos(metadatos):
    """Cuenta las hojas del árbol (también recursiva)."""
    if not isinstance(metadatos, dict):
        return 1
    return sum(contar_campos(v) for v in metadatos.values())


def cargar_metadatos(ruta):
    """Lee el CSV clave,valor y devuelve el diccionario anidado."""
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró {ruta}")
    df = pd.read_csv(ruta, keep_default_na=False)
    if list(df.columns[:2]) != ["clave", "valor"]:
        raise KeyError("El archivo debe tener las columnas 'clave' y 'valor'.")
    return anidar(dict(zip(df["clave"], df["valor"])))


def verificar_antes_de_guardar(metadatos):
    """Lanza ValueError si quedan campos vacíos o pendientes."""
    pendientes = buscar_pendientes(metadatos)
    if pendientes:
        raise ValueError("Metadatos incompletos: " + ", ".join(pendientes))
    return True


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parents[1]
    meta = cargar_metadatos(raiz / "docs" / "metadatos_proyecto.csv")
    print(f"Campos en el árbol: {contar_campos(meta)}")
    print("Pendientes:", buscar_pendientes(meta) or "ninguno")
    prueba = {"datos": {"archivo": "x.csv", "fuente": {"autor": "", "url": "PENDIENTE"}}}
    print("Prueba con huecos:", buscar_pendientes(prueba))
