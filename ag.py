"""Punto de entrada independiente para el Algoritmo Genético (AG)."""

import argparse
import time
from pathlib import Path

from src.ag_build import ejecutar_algoritmo_genetico
from src.operadores import leer_instancia_taillard
from src.salidas import guardar_resultado

RAIZ = Path(__file__).resolve().parent


def crear_parser():
    parser = argparse.ArgumentParser(description="Resuelve una instancia PFSP mediante Algoritmo Genético.")
    parser.add_argument("instancia", help="Archivo Taillard (nombre en data/ o ruta).")
    parser.add_argument("--poblacion", type=int, default=40)
    parser.add_argument("--iteraciones", type=int, default=200)
    parser.add_argument("--cruce", type=float, default=0.9)
    parser.add_argument("--mutacion", type=float, default=0.15)
    parser.add_argument("--semilla", type=int, default=42)
    parser.add_argument("--salida", default="resultados/ag.csv")
    return parser


def resolver_ruta(ruta):
    candidata = Path(ruta)
    return candidata if candidata.is_file() else RAIZ / "data" / ruta


def main():
    args = crear_parser().parse_args()
    instancia = leer_instancia_taillard(resolver_ruta(args.instancia))
    inicio = time.perf_counter()
    permutacion, makespan, historia = ejecutar_algoritmo_genetico(
        instancia.datos, args.poblacion, args.cruce, args.mutacion, args.iteraciones, args.semilla, True
    )
    fila = guardar_resultado(RAIZ / args.salida, "AG", instancia.nombre, makespan, permutacion,
                            instancia.metadatos.get("mejor_conocido"), time.perf_counter() - inicio)
    print(f"AG | {instancia.nombre} | C_max={makespan} | RPD={fila['rpd_porcentaje']}%")
    print(f"Resultado: {RAIZ / args.salida}")
    return historia


if __name__ == "__main__":
    main()
