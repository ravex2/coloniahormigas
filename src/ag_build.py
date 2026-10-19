"""Operadores y ejecuciones del algoritmo genético y memético para PFSP."""

from __future__ import annotations

import random
from typing import Callable

import numpy as np

from src.operadores import calcular_makespan

from dataclasses import dataclass
from typing import Callable, Optional


def crear_poblacion(trabajos: int, tamano: int, rng: random.Random) -> list[np.ndarray]:
    base = list(range(trabajos))
    return [np.asarray(rng.sample(base, trabajos), dtype=np.int64) for _ in range(tamano)]


def seleccion_torneo(poblacion, tiempos, rng: random.Random, tamano: int = 3) -> np.ndarray:
    candidatos = rng.sample(poblacion, min(tamano, len(poblacion)))
    return min(candidatos, key=lambda individuo: calcular_makespan(individuo, tiempos))


def cruce_ordenado(padre_a: np.ndarray, padre_b: np.ndarray, rng: random.Random) -> np.ndarray:
    inicio, fin = sorted(rng.sample(range(len(padre_a)), 2))
    hijo = np.full(len(padre_a), -1, dtype=np.int64)
    hijo[inicio:fin] = padre_a[inicio:fin]
    usados = set(hijo[inicio:fin].tolist())
    hijo[hijo == -1] = [gen for gen in padre_b if int(gen) not in usados]
    return hijo


def mutacion_intercambio(individuo: np.ndarray, probabilidad: float, rng: random.Random) -> None:
    if rng.random() < probabilidad:
        primero, segundo = rng.sample(range(len(individuo)), 2)
        individuo[primero], individuo[segundo] = individuo[segundo], individuo[primero]


    

def _ejecutar_evolutivo(tiempos, tam_pob, prob_cruce, prob_mutacion, iteraciones, semilla,
                        mejora_local: Callable | None = None, frecuencia_local: int = 1,
                        retornar_historia: bool = False, semilla_inicial=None, observador=None):

    
    if tam_pob < 2 or iteraciones < 1:
        raise ValueError("La población debe ser >= 2 y las iteraciones >= 1.")
    if not 0 <= prob_cruce <= 1 or not 0 <= prob_mutacion <= 1:
        raise ValueError("Las probabilidades deben estar entre 0 y 1.")
    
    rng = random.Random(semilla)
    poblacion = crear_poblacion(tiempos.shape[1], tam_pob, rng)
    
    if semilla_inicial is not None:
        poblacion[0] = semilla_inicial.copy()
    
    mejor = min(poblacion, key=lambda x: calcular_makespan(x, tiempos)).copy()
    mejor_costo = calcular_makespan(mejor, tiempos)
    historia = [mejor_costo]
    
    # Copias serializables: observar no modifica la población ni consume azar.
    def emitir(generacion):
        if observador is not None:
            observador(dict(iteracion=generacion, ruta=mejor.tolist(), costo=int(mejor_costo),
                            poblacion=[x.tolist() for x in poblacion]))
    emitir(0)

    for generacion in range(1, iteraciones + 1):
        nueva = [mejor.copy()]  # elitismo

        while len(nueva) < tam_pob:
            padre_a = seleccion_torneo(poblacion, tiempos, rng)
            padre_b = seleccion_torneo(poblacion, tiempos, rng)
            hijo = cruce_ordenado(padre_a, padre_b, rng) if rng.random() < prob_cruce else padre_a.copy()
            mutacion_intercambio(hijo, prob_mutacion, rng)
            nueva.append(hijo)
        
        poblacion = nueva
        indice, candidato = min(enumerate(poblacion), key=lambda par: calcular_makespan(par[1], tiempos))
        
        if mejora_local and generacion % frecuencia_local == 0:
            candidato = mejora_local(candidato, tiempos, rng)
            poblacion[indice] = candidato
        costo = calcular_makespan(candidato, tiempos)
        
        if costo < mejor_costo:
            mejor, mejor_costo = candidato.copy(), costo
        historia.append(mejor_costo)
        emitir(generacion)
    return (mejor, mejor_costo, historia) if retornar_historia else (mejor, mejor_costo)


def ejecutar_algoritmo_genetico(tiempos, tam_pob, por_cru, por_mul, num_ite, semilla, retornar_historia=False, observador=None):
    return _ejecutar_evolutivo(tiempos, tam_pob, por_cru, por_mul, num_ite, semilla, retornar_historia=retornar_historia, observador=observador)
