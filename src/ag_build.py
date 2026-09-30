import numpy as np
import random

from src.pfsp import fitness_pfsp

''' 
Implementacion de Metaheuristicas para PFSP: Algoritmo Genetico Puro y Algoritmo Memetico
'''

def crear_poblacion(cantidad_trabajos, tam_pob, generador):
    poblacion = []
    plantilla = np.arange(cantidad_trabajos, dtype=np.int64)
    for _ in range(tam_pob):
        individuo = plantilla.copy()
        individuo = np.array(generador.sample(individuo.tolist(), cantidad_trabajos))
        poblacion.append(individuo)
    return poblacion

def seleccion_torneo(poblacion, tiempos, generador, tam_torneo=3):
    participantes = generador.sample(
        poblacion,
        min(tam_torneo, len(poblacion)),
    )
    return min(participantes, key=lambda individuo: fitness_pfsp(individuo, tiempos))

def cruce_ordenado(primer_padre, segundo_padre, generador):
    inicio, fin = sorted(generador.sample(range(len(primer_padre)), 2))
    hijo = np.full(len(primer_padre), -1, dtype=np.int64)
    hijo[inicio:fin] = primer_padre[inicio:fin]
    genes_restantes = [
        trabajo for trabajo in segundo_padre if trabajo not in hijo[inicio:fin]
    ]

    posicion = 0
    for indice in range(len(hijo)):
        if hijo[indice] == -1:
            hijo[indice] = genes_restantes[posicion]
            posicion += 1
    return hijo

def mutar_intercambio(individuo, por_mul, generador):
    if generador.random() < por_mul:
        primera, segunda = generador.sample(range(len(individuo)), 2)
        individuo[primera], individuo[segunda] = (
            individuo[segunda],
            individuo[primera],
        )

def busqueda_local_insercion(individuo, tiempos, generador, max_evaluaciones=100):
    """Primera mejora por insercion, limitada por evaluaciones de vecinos."""
    mejor = individuo.copy()
    costo = fitness_pfsp(mejor, tiempos)
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
                valor = fitness_pfsp(vecino, tiempos)
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


def ejecutar_algoritmo_genetico(
    tiempos,
    tam_pob,
    por_cru,
    por_mul,
    num_ite,
    semilla,
    retornar_historia=False,
):
    """Algoritmo Genetico Puro (exploracion sin busqueda local)."""
    generador = random.Random(semilla)
    cantidad_trabajos = tiempos.shape[1]
    poblacion = crear_poblacion(cantidad_trabajos, tam_pob, generador)

    mejor = min(poblacion, key=lambda individuo: fitness_pfsp(individuo, tiempos))
    mejor_costo = fitness_pfsp(mejor, tiempos)

    historia = [mejor_costo] if retornar_historia else None

    for generacion in range(num_ite):
        nueva_poblacion = [mejor.copy()]
        while len(nueva_poblacion) < tam_pob:
            primer_padre = seleccion_torneo(poblacion, tiempos, generador)
            segundo_padre = seleccion_torneo(poblacion, tiempos, generador)

            if generador.random() < por_cru:
                hijo = cruce_ordenado(primer_padre, segundo_padre, generador)
            else:
                hijo = primer_padre.copy()

            mutar_intercambio(hijo, por_mul, generador)
            nueva_poblacion.append(hijo)

        poblacion = nueva_poblacion
        candidato = min(
            poblacion,
            key=lambda individuo: fitness_pfsp(individuo, tiempos),
        )
        candidato_costo = fitness_pfsp(candidato, tiempos)
        if candidato_costo < mejor_costo:
            mejor = candidato.copy()
            mejor_costo = candidato_costo

        if retornar_historia:
            historia.append(mejor_costo)

    if retornar_historia:
        return mejor, mejor_costo, historia
    return mejor, mejor_costo


def ejecutar_algoritmo_memetico(
    tiempos,
    tam_pob,
    por_cru,
    por_mul,
    num_ite,
    semilla,
    frecuencia_local=1,
    max_evaluaciones_local=100,
    retornar_historia=False,
):
    """Algoritmo Memetico (Algoritmo Genetico + Busqueda Local por Insercion)."""
    generador = random.Random(semilla)
    cantidad_trabajos = tiempos.shape[1]
    poblacion = crear_poblacion(cantidad_trabajos, tam_pob, generador)

    mejor = min(poblacion, key=lambda individuo: fitness_pfsp(individuo, tiempos))
    mejor_costo = fitness_pfsp(mejor, tiempos)

    historia = [mejor_costo] if retornar_historia else None

    for generacion in range(num_ite):
        nueva_poblacion = [mejor.copy()]
        while len(nueva_poblacion) < tam_pob:
            primer_padre = seleccion_torneo(poblacion, tiempos, generador)
            segundo_padre = seleccion_torneo(poblacion, tiempos, generador)

            if generador.random() < por_cru:
                hijo = cruce_ordenado(primer_padre, segundo_padre, generador)
            else:
                hijo = primer_padre.copy()

            mutar_intercambio(hijo, por_mul, generador)
            nueva_poblacion.append(hijo)

        poblacion = nueva_poblacion
        candidato = min(
            poblacion,
            key=lambda individuo: fitness_pfsp(individuo, tiempos),
        )

        if frecuencia_local > 0 and (generacion + 1) % frecuencia_local == 0:
            mejorado = busqueda_local_insercion(
                candidato, tiempos, generador, max_evaluaciones_local
            )
            for i, individuo in enumerate(poblacion):
                if np.array_equal(individuo, candidato):
                    poblacion[i] = mejorado
                    break
            candidato = mejorado

        candidato_costo = fitness_pfsp(candidato, tiempos)
        if candidato_costo < mejor_costo:
            mejor = candidato.copy()
            mejor_costo = candidato_costo

        if retornar_historia:
            historia.append(mejor_costo)

    if retornar_historia:
        return mejor, mejor_costo, historia
    return mejor, mejor_costo