# Arquitectura de la Fase 3

## Flujo de datos

    data/raw (crudo, fuera del repositorio)
        │  src/carga.py: cargar_datos → eliminar_columnas → eliminar_filas_nulas
        ▼
    DataFrame limpio (46.433 × 7)
        │  src/pipeline.py: Pipeline([TratamientoAnio, CodificadorOneHot,
        │                              TransformacionLog, CreacionMoroso])
        ▼
    DataFrame procesado (46.433 × 31)  ==  archivo de F2 (assert_frame_equal)
        │  partición estratificada por moroso (semilla 42, 20 % prueba)
        ▼
    data/processed: entrenamiento_f3, prueba_f3, diccionario_f3, parametros_f3  →  Fase 4

## Componentes

| Componente | Responsabilidad | Archivo |
| --- | --- | --- |
| Funciones de carga | Leer el crudo y limpiarlo sin modificar el original | `src/carga.py` |
| `Transformador` | Contrato común (`ajustar`, `transformar`) y estado privado | `src/transformadores.py` |
| `TratamientoAnio` y estrategias | Tratar el año faltante (Strategy) | `src/transformadores.py` |
| `CodificadorOneHot` | Codificación binaria con esquema fijo | `src/transformadores.py` |
| `TransformacionLog` | Reducir la asimetría de los montos | `src/transformadores.py` |
| `CreacionMoroso` | Crear la variable objetivo | `src/transformadores.py` |
| `Pipeline` | Ejecutar los pasos en orden con la misma llamada | `src/pipeline.py` |
| Mediciones | Tiempo y memoria | `src/medicion.py` |
| Revisión de metadatos | Recorrido recursivo para detectar campos vacíos o pendientes | `src/recursion.py` |
| Notebook de F3 | Demostrar, comparar y guardar las salidas | `F3/notebook_f3.ipynb` |

**Cohesión y acoplamiento.** Cada módulo responde a una sola tarea. `carga.py` no conoce las clases; el `Pipeline` solo depende de la interfaz `Transformador`, no de cada transformador concreto.

## Patrón Strategy: tratamiento del año faltante

`TratamientoAnio` recibe una estrategia (`EstrategiaAnio`) que decide cómo tratar las 691 filas sin año de patente. El pipeline no cambia al elegir otra.

| Estrategia | Qué hace | Nulos en `ANIO_PATENTE` | Idéntico a F2 |
| --- | --- | --- | --- |
| `RellenarConValor(0)` | Rellena con 0 (lo que hizo F2) | 0 | Sí |
| `DejarNulo` | Deja el valor nulo | 691 | No |
| `MedianaPorTesoreria` | Imputa la mediana del año por tesorería | 0 | No |

**Por qué Strategy.** El tratamiento del año faltante es la decisión de modelado más discutible del proceso, y puede cambiar. Con Strategy se prueba otra alternativa sin tocar el pipeline ni los demás transformadores (principio abierto/cerrado), y cada alternativa se prueba por separado. La alternativa más simple, un `if` dentro de `TratamientoAnio` por cada caso, mezclaría las reglas en una sola clase y habría que modificarla cada vez que se agregue una.

**Decisión.** Se mantiene `RellenarConValor(0)` por defecto porque reproduce F2 y deja el resultado trazable frente a la fase anterior. El indicador `anio_faltante` conserva qué filas venían sin dato, de modo que el 0 no se confunde con un año real.

## Función recursiva

`src/recursion.py` convierte los metadatos (`docs/metadatos_proyecto.csv`, claves como `datos.fuente.autor`) en un diccionario anidado y lo recorre con `buscar_pendientes`.

- **Caso base:** el valor no es un diccionario (una hoja): se revisa si está vacío, es nulo o dice "pendiente".
- **Caso recursivo:** el valor es un diccionario: se llama de nuevo a la función sobre cada hijo, acumulando la ruta (`datos.fuente.autor`).

Con los metadatos actuales (20 campos) no hay pendientes. Con `{"datos": {"fuente": {"autor": "", "url": "PENDIENTE"}}}` devuelve `['datos.fuente.autor', 'datos.fuente.url']`. `verificar_antes_de_guardar` lanza `ValueError` si queda alguno, para no guardar metadatos incompletos. La recursión es adecuada aquí porque la profundidad de los metadatos no está fijada de antemano.

## Escalabilidad: si llega el archivo de 2026

El diseño separa lo que cambia de lo que no. Si el nuevo archivo mantiene el esquema de columnas:

| Qué cambia | Dónde |
| --- | --- |
| Nombre y ruta del archivo | Argumento de `cargar_datos` en el notebook; actualizar `datos.archivo` y las fechas en `docs/metadatos_proyecto.csv` |
| Conteos de filas y de nulos | Se recalculan solos al ejecutar; revisar con `src/recursion.py` que los metadatos no queden con campos pendientes |
| Años nuevos (2026) | `TratamientoAnio` y las estrategias no requieren cambios; la mediana se aprende en el ajuste |
| Tesorerías o tipos de persona nuevos | `CodificadorOneHot` usa un esquema fijo (diccionario categoría → columna). Si el archivo de 2026 trae una categoría que no está en el diccionario, `ajustar` falla con un error que la nombra; se agrega al diccionario y las columnas siguen saliendo en el mismo orden. En `transformar`, una categoría no vista queda en ceros sin lanzar error |

No hay que modificar `Pipeline`, `Transformador`, `TransformacionLog` ni `CreacionMoroso`. Si el esquema de columnas cambiara, se tocaría solo `src/carga.py` (qué columnas se eliminan) y la lista de columnas requeridas del transformador afectado. Si el archivo creciera mucho, las mediciones de `src/medicion.py` muestran que la versión vectorizada y `groupby` escalan en O(n) y son mucho más rápidas que los bucles en Python; el recorrido con diccionario solo convendría si la memoria fuera la restricción.
