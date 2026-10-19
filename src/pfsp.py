"""Modelo y utilidades del Permutation Flow Shop Scheduling Problem (PFSP)."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence, TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from src.operadores import Instancia


def leer_instancia_taillard(ruta: str | Path) -> Instancia:
    """Lee una instancia Taillard; su matriz queda indexada como [máquina, trabajo]."""
    # Importación al leer: operadores también expone las funciones de este módulo.
    # Así ambos pueden importarse primero sin provocar un ciclo de inicialización.
    from src.operadores import Instancia, TipoProblema

    ruta = Path(ruta)
    with ruta.open(encoding="utf-8") as archivo:
        archivo.readline()
        metadatos = archivo.readline().split("#", 1)[-1].split()
        archivo.readline()
        trabajos, maquinas = map(int, archivo.readline().split())
        archivo.readline()
        # pandas interpreta las columnas; NumPy conserva el formato numérico del motor.
        tiempos = pd.read_table(archivo, sep=r"\s+", header=None, dtype=np.int64).to_numpy()
    if tiempos.shape != (maquinas, trabajos):
        raise ValueError(f"La matriz de {ruta.name} tiene forma {tiempos.shape}; se esperaba ({maquinas}, {trabajos}).")
    return Instancia(
        nombre=ruta.stem,
        tipo=TipoProblema.PFSP,
        datos=tiempos,
        metadatos={
            "trabajos": trabajos,
            "maquinas": maquinas,
            "semilla_origen": int(metadatos[2]),
            "mejor_conocido": int(metadatos[3]),
            "cota_inferior": int(metadatos[4]),
        },
    )


def validar_permutacion(permutacion: Sequence[int], trabajos: int) -> np.ndarray:
    permutacion = np.asarray(permutacion, dtype=np.int64)
    if permutacion.ndim != 1 or len(permutacion) != trabajos:
        raise ValueError(f"La solución debe contener exactamente {trabajos} trabajos.")
    if not np.array_equal(np.sort(permutacion), np.arange(trabajos)):
        raise ValueError("La solución debe ser una permutación válida de los trabajos.")
    return permutacion


def calcular_makespan(permutacion: Sequence[int], tiempos: np.ndarray) -> int:
    """Calcula C_max de una permutación en un flow shop permutacional."""
    permutacion = validar_permutacion(permutacion, tiempos.shape[1])
    return calcular_makespan_parcial(permutacion, tiempos)

# Cálculo reutilizable para secuencias parciales, empleado por la heurística NEH.
def calcular_makespan_parcial(secuencia: Sequence[int], tiempos: np.ndarray) -> int:
    """Calcula el tiempo de finalización de una secuencia, incluso si es parcial."""
    secuencia = np.asarray(secuencia, dtype=np.int64)
    final_maquina = np.zeros(tiempos.shape[0], dtype=np.int64)
    for trabajo in secuencia:
        final_trabajo = 0
        for maquina in range(tiempos.shape[0]):
            final_trabajo = max(final_trabajo, int(final_maquina[maquina])) + int(tiempos[maquina, trabajo])
            final_maquina[maquina] = final_trabajo
    return int(final_maquina[-1])


fitness_pfsp = calcular_makespan

