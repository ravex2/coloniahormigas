"""Implementación del Algoritmo Memético (AM) y su búsqueda local para PFSP."""

import random

import numpy as np

from src.ag_build import _ejecutar_evolutivo
from src.operadores import calcular_makespan, calcular_makespan_parcial


''' mejora 1'''
def heuristica_neh(tiempos: np.ndarray) -> np.ndarray:
    """Construye una solución inicial NEH antes de iniciar la fase memética."""
    orden = sorted(range(tiempos.shape[1]), key=lambda trabajo: (-int(tiempos[:, trabajo].sum()), trabajo))
    secuencia: list[int] = []
    for trabajo in orden:
        candidatos = []
        for posicion in range(len(secuencia) + 1):
            candidata = secuencia.copy()
            candidata.insert(posicion, trabajo)
            candidatos.append(candidata)
        secuencia = min(candidatos, key=lambda x: calcular_makespan_parcial(x, tiempos))
    return np.asarray(secuencia, dtype=np.int64)


def busqueda_local_insercion_anterior(individuo, tiempos, generador, max_evaluaciones=100):
    """Primera mejora por insercion, limitada por evaluaciones de vecinos."""
    mejor = individuo.copy()
    costo = calcular_makespan(mejor, tiempos)
    evaluaciones = 0
    while evaluaciones < max_evaluaciones:
        mejora = False
        origenes = list(range(len(mejor)))
        generador.shuffle(origenes)
        for origen in origenes:
            destinos = list(range(len(mejor)))
            generador.shuffle(destinos)
            for destino in destinos:
                if origen == destino:
                    continue
                vecino = mejor.tolist()
                vecino.insert(destino, vecino.pop(origen))
                vecino = np.array(vecino, dtype=np.int64)
                valor = calcular_makespan(vecino, tiempos)
                evaluaciones += 1
                if valor < costo:
                    mejor, costo, mejora = vecino, valor, True
                    break
                if evaluaciones >= max_evaluaciones:
                    return mejor
            if mejora:
                break
        if not mejora:
            break
    return mejor

def busqueda_local_insercion(individuo, tiempos, rng: random.Random | None = None,
                             max_evaluaciones: int = 1000, max_pases: int = 5):
    """Aplica inserciones de mejor mejora; nunca conserva un vecino peor."""
    mejor, mejor_costo, evaluaciones = individuo.copy(), calcular_makespan(individuo, tiempos), 0
    for _ in range(max_pases):
        candidato, costo_candidato = mejor, mejor_costo
        for origen in range(len(mejor)):
            for destino in range(len(mejor)):
                if origen == destino:
                    continue
                vecino = mejor.tolist()
                vecino.insert(destino, vecino.pop(origen))
                vecino = np.asarray(vecino, dtype=np.int64)
                evaluaciones += 1
                costo = calcular_makespan(vecino, tiempos)
                if costo < costo_candidato:
                    candidato, costo_candidato = vecino, costo
                if evaluaciones >= max_evaluaciones:
                    break
            if evaluaciones >= max_evaluaciones:
                break
        if costo_candidato >= mejor_costo:
            break
        mejor, mejor_costo = candidato, costo_candidato
    return mejor


def ejecutar_algoritmo_memetico(tiempos, tam_pob, por_cru, por_mul, num_ite, semilla,
                                frecuencia_local=1, max_evaluaciones_local=1000,
                                retornar_historia=False, observador=None):
    """AG con elitismo, solución NEH inicial y búsqueda local por inserción."""
    if frecuencia_local < 1:
        raise ValueError("La frecuencia de búsqueda local debe ser >= 1.")

    def mejorar(individuo, matriz, rng):
        return busqueda_local_insercion(individuo, matriz, rng, max_evaluaciones_local)

    inicial = busqueda_local_insercion(
        heuristica_neh(tiempos), tiempos, max_evaluaciones=max_evaluaciones_local
    )
    return _ejecutar_evolutivo(
        tiempos, tam_pob, por_cru, por_mul, num_ite, semilla, mejorar,
        frecuencia_local, retornar_historia, inicial, observador,
    )
