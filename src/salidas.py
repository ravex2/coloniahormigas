"""Persistencia sencilla y consistente de resultados experimentales."""

from __future__ import annotations

import pandas as pd
from pathlib import Path


def guardar_resultado(ruta, algoritmo, instancia, makespan, permutacion, mejor_conocido, segundos,
                      nombre_metrica="makespan"):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    rpd = "" if mejor_conocido is None else round((makespan - mejor_conocido) * 100 / mejor_conocido, 4)
    fila = {
        "algoritmo": algoritmo, "instancia": instancia, nombre_metrica: makespan,
        "mejor_conocido": mejor_conocido or "", "rpd_porcentaje": rpd,
        "segundos": round(segundos, 6), "permutacion_1_indexada": " ".join(str(x + 1) for x in permutacion),
    }
    # Sin índice adicional: conserva las columnas del formato de resultados existente.
    pd.DataFrame([fila]).to_csv(ruta, index=False, encoding="utf-8")
    return fila
