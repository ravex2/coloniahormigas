"""Ant Colony System (ACS)
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.operadores import calcular_makespan, Instancia, TipoProblema

'''
Podria separarse pero en este caso, si usamos el dataset de tailward y el otro usamos 
'''
def funcion_costos(ruta, datos, tipo=TipoProblema.PFSP):
    """Evalúa una solución: makespan PFSP o longitud del ciclo TSP"""
    if tipo == TipoProblema.PFSP:
        return calcular_makespan(ruta, datos)
    if tipo == TipoProblema.TSP:
        return longitud_tour_hormiga(ruta, datos)
    raise ValueError(f"Tipo de problema no soportado: {tipo}")


def calcular_heuristica(datos, tipo=TipoProblema.PFSP):
    """Calcula visibilidad: inverso de carga por trabajo o distancia por arco."""
    if tipo == TipoProblema.PFSP:
        return 1.0 / np.maximum(datos.sum(axis=0, dtype=float), 1.0)
    if tipo == TipoProblema.TSP:
        # La diagonal no representa desplazamientos válidos; evita dividir por cero.
        return np.divide(1.0, datos, out=np.zeros_like(datos, dtype=float), where=datos > 0)
    raise ValueError(f"Tipo de problema no soportado: {tipo}")


def inicializar_feromona(datos, tipo=TipoProblema.PFSP):
    """Devuelve la matriz tau y tau0 a partir del costo del orden natural."""
    nodos = datos.shape[1]
    referencia = np.arange(nodos, dtype=np.int64)
    tau0 = 1.0 / max(funcion_costos(referencia, datos, tipo) * nodos, 1.0)
    # PFSP añade una fila para el nodo artificial de salida.
    filas = nodos + 1 if tipo == TipoProblema.PFSP else nodos
    feromona = np.full((filas, nodos), tau0, dtype=float)
    if tipo == TipoProblema.TSP:
        np.fill_diagonal(feromona, 0.0)
    return feromona, tau0


def construir_colonia(datos, hormigas, feromona, heuristica, alpha, beta, q0,
                      tau0, rng, tipo=TipoProblema.PFSP):
    """Construye y evalúa una ruta por hormiga para una iteración de ACS.
    """
    nodos = datos.shape[1]
    soluciones = []
    for _ in range(hormigas):
        inicio = int(rng.integers(nodos)) if tipo == TipoProblema.TSP else nodos
        ruta = [inicio] if tipo == TipoProblema.TSP else []
        disponibles = [nodo for nodo in range(nodos) if nodo != inicio]
        actual = inicio
        while disponibles:
            siguiente = regla_transicion(actual, disponibles, feromona, heuristica, beta, q0, rng)
            actualizar_feromona_local(feromona, actual, siguiente, alpha, tau0)
            ruta.append(siguiente)
            disponibles.remove(siguiente)
            actual = siguiente
        if tipo == TipoProblema.TSP:
            # El regreso también recibe actualización local; no repetimos el nodo en la permutación.
            actualizar_feromona_local(feromona, actual, inicio, alpha, tau0)
        solucion = np.asarray(ruta, dtype=np.int64)
        soluciones.append((solucion, funcion_costos(solucion, datos, tipo)))
    return soluciones


"""Aplica la regla de transición ACS de las ecuaciones (1) y (2).
"""
def regla_transicion(actual, disponibles, feromona, heuristica, beta, q0, rng):

    indices = np.asarray(disponibles, dtype=np.intp)
    visibilidad = heuristica[actual, indices] if heuristica.ndim == 2 else heuristica[indices]
    pesos = feromona[actual, indices] * np.power(visibilidad, beta)

    # Ecuación (1): explotación, j0 = argmax(tau_ij * eta_ij^beta).
    if rng.random() <= q0:
        return disponibles[int(np.argmax(pesos))]

    # Ecuación (2): ruleta. Si un caso numérico invalida los pesos, se explora uniforme.
    total = float(pesos.sum())
    if total <= 0 or not np.isfinite(total):
        return disponibles[int(rng.integers(len(disponibles)))]
    return disponibles[int(rng.choice(len(disponibles), p=pesos / total))]


def actualizar_feromona_local(feromona, origen, destino, alpha, tau0):
    feromona[origen, destino] = (1 - alpha) * feromona[origen, destino] + alpha * tau0


def actualizar_feromona_global(feromona, ruta, mejor_costo, alpha, inicio=None, cerrar_ciclo=False):
    """Ecuación (3): evapora todos los arcos y refuerza solo la mejor ruta global.

    Para un arco fuera de la mejor solución, Delta es cero. Para uno que pertenece
    a ella, Delta vale ``1 / C_max(mejor)``: una solución más corta deja más feromona.
    """
    # Parte (1-alpha) * tau(t-1) de la ecuación global para todos los arcos.
    feromona *= 1 - alpha

    # Parte alpha * Delta: solo los arcos de la mejor ruta reciben refuerzo positivo.
    deposito = 1.0 / mejor_costo
    recorrido = ([inicio] if inicio is not None else []) + ruta.tolist()
    if cerrar_ciclo:
        recorrido.append(ruta[0])
    for origen, destino in zip(recorrido, recorrido[1:]):
        feromona[origen, destino] += alpha * deposito



'''
Integracion con problema de PFSP
ACS con las fórmulas de transición y feromona 
'''
def ejecutar_acs(tiempos, hormigas, iteraciones, alpha, beta, q0, semilla,
                 retornar_historia=False):
    if hormigas < 1 or iteraciones < 1:
        raise ValueError("El número de hormigas e iteraciones debe ser >= 1.")
    if not 0 <= alpha <= 1 or beta < 0 or not 0 <= q0 <= 1:
        raise ValueError("alpha y q0 deben estar en [0, 1]; beta no puede ser negativo.")

    trabajos = tiempos.shape[1]
    rng = np.random.default_rng(semilla)

    # eta_j: visibilidad del trabajo j. Menor carga total implica mayor deseabilidad.
    heuristica = calcular_heuristica(tiempos)

    # tau0 es la feromona inicial mencionada por la actualización local del PDF.
    feromona, tau0 = inicializar_feromona(tiempos)

    # El último índice es un nodo artificial desde el cual todas las hormigas empiezan.
    inicio = trabajos
    mejor_global, mejor_costo, historia = None, float("inf"), []

    for _ in range(iteraciones):
        soluciones = construir_colonia(
            tiempos, hormigas, feromona, heuristica, alpha, beta, q0, tau0, rng
        )

        candidata, costo = min(soluciones, key=lambda par: par[1])
        if costo < mejor_costo:
            mejor_global, mejor_costo = candidata.copy(), costo

        actualizar_feromona_global(feromona, mejor_global, mejor_costo, alpha, inicio)
        historia.append(int(mejor_costo))

    return (mejor_global, int(mejor_costo), historia) if retornar_historia else (mejor_global, int(mejor_costo))



''' leer berlink '''
def leer_tsplib(ruta, mejor_conocido=None):
    """Lee un dataset TSPLIB de coordenadas y devuelve una instancia general."""
    with open(ruta, encoding="utf-8") as archivo:
        lineas = archivo.read().splitlines()
    inicio, fin = lineas.index("NODE_COORD_SECTION"), lineas.index("EOF")

    tabla = pd.read_table(ruta, header=None, sep=r"\s+", skiprows=inicio + 1, nrows=fin - inicio - 1)
    coordenadas = tabla.drop(columns=0).to_numpy(dtype=float)
    if coordenadas.ndim != 2 or coordenadas.shape[1] != 2:
        raise ValueError("El dataset TSPLIB debe contener coordenadas x e y.")
    nombre = str(ruta).rsplit("/", 1)[-1].rsplit(".", 1)[0]
    return Instancia(nombre, TipoProblema.TSP, coordenadas, {
        "nodos": len(coordenadas), "mejor_conocido": mejor_conocido,
    })


def leer_berlin52(ruta):
    """Atajo para Berlin52, cuyo mejor tour conocido tiene distancia 7542."""
    return leer_tsplib(ruta, mejor_conocido=7542)


def matriz_distancias(coordenadas):
    diferencias = coordenadas[:, np.newaxis, :] - coordenadas[np.newaxis, :, :]
    return np.linalg.norm(diferencias, axis=2)


def longitud_tour_hormiga(tour, distancias):
    """Suma cada arista del tour y la arista final que vuelve al nodo inicial."""
    # roll empareja cada nodo con su sucesor e incluye el cierre del ciclo.
    tour = np.asarray(tour, dtype=np.intp)
    return float(distancias[tour, np.roll(tour, -1)].sum())


'''
# entrenamiento con dataset de berlin

'''
def ejecutar_acs_berlin52(coordenadas, hormigas, iteraciones, alpha, beta, q0, semilla,
                          retornar_historia=False, observador=None):

    if hormigas < 1 or iteraciones < 1:
        raise ValueError("El número de hormigas e iteraciones debe ser >= 1.")
    if not 0 <= alpha <= 1 or beta < 0 or not 0 <= q0 <= 1:
        raise ValueError("alpha y q0 deben estar en [0, 1]; beta no puede ser negativo.")

    nodos = len(coordenadas)
    distancias = matriz_distancias(coordenadas)
    rng = np.random.default_rng(semilla)

    heuristica = calcular_heuristica(distancias, TipoProblema.TSP)
    feromona, tau0 = inicializar_feromona(distancias, TipoProblema.TSP)
    mejor_global, mejor_costo, historia = None, float("inf"), []

    for _ in range(iteraciones):
        soluciones = construir_colonia(
            distancias, hormigas, feromona, heuristica, alpha, beta, q0, tau0, rng,
            TipoProblema.TSP,
        )

        candidata, costo = min(soluciones, key=lambda par: par[1])
        if costo < mejor_costo:
            mejor_global, mejor_costo = candidata.copy(), costo
        actualizar_feromona_global(feromona, mejor_global, mejor_costo, alpha, cerrar_ciclo=True)
        historia.append(mejor_costo)
        if observador is not None:
            observador(dict(iteracion=len(historia), ruta=mejor_global.tolist(),
                            costo=float(mejor_costo),
                            poblacion=[tour.tolist() for tour, _ in soluciones],
                            feromona=feromona.tolist()))

    return (mejor_global, mejor_costo, historia) if retornar_historia else (mejor_global, mejor_costo)
