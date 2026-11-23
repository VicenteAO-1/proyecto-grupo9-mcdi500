# Mediciones de eficiencia (Fase 3, II.d)

Mediciones sobre las 46.433 filas procesadas, ejecutadas con `python src/medicion.py` (código en `src/medicion.py`).
Tiempo: `timeit` con 7 repeticiones de 5 llamadas, conservando el **menor** tiempo por llamada.
Memoria: pico de memoria asignada en una llamada, medido con `tracemalloc`.
En ambas comparaciones las dos versiones dan **el mismo resultado** (el programa se detiene si no coinciden).

## Comparación 1: variable `moroso`

| Versión | Tiempo (s) | Memoria (MiB) | Complejidad temporal | Complejidad espacial |
| --- | --- | --- | --- | --- |
| Bucle fila a fila (`moroso_bucle`) | 0,008336 | 2,947 | O(n) en Python | O(n) |
| Vectorizada (`moroso_vectorizado`) | 0,000106 | 0,402 | O(n) en C (NumPy) | O(n) |

La versión vectorizada es 78,5 veces más rápida y usa menos memoria (el bucle construye una lista de Python antes de pasarla a una Serie).

**Decisión:** se usa la versión vectorizada (`SALDO > 0`), que es la que está en `CreacionMoroso`. Ambas son O(n), pero el recorrido en C evita el costo de ejecutar el bucle en Python.

## Comparación 2: tasa de morosidad por tesorería

| Versión | Tiempo (s) | Memoria (MiB) | Complejidad temporal | Complejidad espacial |
| --- | --- | --- | --- | --- |
| Diccionario recorrido a mano (`tasa_diccionario`) | 0,018824 | 0,011 | O(n) en Python | O(k) |
| `groupby` (`tasa_groupby`) | 0,004338 | 2,268 | O(n) en C | O(n) |

(k = 18 tesorerías, n = 46.433 filas.)

`groupby` es 4,3 veces más rápido, pero usa más memoria porque crea estructuras intermedias del tamaño de los datos. El diccionario guarda solo 18 pares de contadores.

**Decisión:** se usa `groupby`. Con 46 mil filas la diferencia de memoria (unos 2 MiB) no es un problema, y la ganancia de tiempo y la claridad del código pesan más. Si los datos crecieran mucho y la memoria fuera la restricción, el diccionario sería la alternativa, porque su memoria depende de las tesorerías (k) y no de las filas (n).

## Conclusión

En las dos comparaciones la versión vectorizada o agrupada es más rápida con el mismo resultado. La complejidad teórica es O(n) en las cuatro versiones; la diferencia está en el factor constante: el recorrido en Python es mucho más lento que en C.
