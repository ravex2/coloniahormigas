"""Benchmark común de AG, AM y ACS sobre instancias Taillard."""

import pandas as pd
import time
from pathlib import Path

from src.acs_build import ejecutar_acs
from src.ag_build import ejecutar_algoritmo_genetico
from src.am_build import ejecutar_algoritmo_memetico
from src.operadores import leer_instancia_taillard

RAIZ = Path(__file__).resolve().parent.parent


CATEGORIAS = {(20, 5): "Pequeña", (50, 10): "Mediana", (100, 10): "Grande"}

''' genera el csv'''
def ejecutar_benchmark(instancias=None, semilla=42, poblacion=30, hormigas=30, iteraciones=100, salida=None):
    if instancias is None:
        # Diez instancias Taillard por tamaño, incluyendo 100x10 (ta071–ta080).
        instancias = [f"ta{i:03d}.txt" for inicio in (1, 41, 71) for i in range(inicio, inicio + 10)]
    resultados = []
    for nombre in instancias:
        instancia = leer_instancia_taillard(RAIZ / "data" / nombre)
        dimensiones = (instancia.metadatos["trabajos"], instancia.metadatos["maquinas"])
        print(f"Evaluando {nombre}: {dimensiones[0]}x{dimensiones[1]}", flush=True)
        configuraciones = {
            "AG": lambda: ejecutar_algoritmo_genetico(instancia.datos, poblacion, 0.9, 0.15, iteraciones, semilla),
            "AM": lambda: ejecutar_algoritmo_memetico(instancia.datos, poblacion, 0.9, 0.15, iteraciones, semilla, frecuencia_local=5),
            "ACS": lambda: ejecutar_acs(instancia.datos, hormigas, iteraciones, 0.1, 2.0, 0.8, semilla),
        }
        fila = {"Instancia": nombre, "Trabajos": instancia.metadatos["trabajos"], "Maquinas": instancia.metadatos["maquinas"],
                "MejorConocido": instancia.metadatos["mejor_conocido"],
                "Categoria": CATEGORIAS.get(dimensiones, "Otra"), "Semilla": semilla,
                "Iteraciones": iteraciones, "Poblacion": poblacion, "Hormigas": hormigas}
        for algoritmo, funcion in configuraciones.items():
            inicio = time.perf_counter()
            _, makespan = funcion()
            fila[f"Makespan_{algoritmo}"] = makespan
            fila[f"RPD_{algoritmo}"] = round((makespan - instancia.metadatos["mejor_conocido"]) * 100 / instancia.metadatos["mejor_conocido"], 4)
            fila[f"Tiempo_{algoritmo}"] = round(time.perf_counter() - inicio, 6)
        resultados.append(fila)
    if not resultados:
        raise ValueError("Debe seleccionar al menos una instancia.")
    salida = Path(salida) if salida is not None else RAIZ / "resultados" / "benchmark_results.csv"
    salida.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(resultados).to_csv(salida, index=False, encoding="utf-8")
    return salida
