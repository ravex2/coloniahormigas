"""Punto de entrada independiente para Ant Colony System (ACS)."""

import argparse
import time
from pathlib import Path

from src.acs_build import ejecutar_acs, ejecutar_acs_berlin52, leer_berlin52
from src.operadores import leer_instancia_taillard
from src.salidas import guardar_resultado

RAIZ = Path(__file__).resolve().parent


def crear_parser():
    parser = argparse.ArgumentParser(description="Resuelve PFSP o el TSP Berlin52 mediante Ant Colony System.")
    parser.add_argument("instancia", help="Archivo Taillard (data/) o Berlin52 (.tsp).")
    parser.add_argument("--hormigas", type=int, default=30)
    parser.add_argument("--iteraciones", type=int, default=200)
    parser.add_argument("--alpha", type=float, default=0.1,
                        help="Factor de evaporación de las actualizaciones local y global.")
    parser.add_argument("--beta", type=float, default=2.0,
                        help="Peso de la heurística en la regla de transición.")
    parser.add_argument("--q0", type=float, default=0.8, help="Probabilidad de explotación.")
    parser.add_argument("--semilla", type=int, default=42)
    parser.add_argument("--salida", default="resultados/acs.csv")
    return parser


def main():
    args = crear_parser().parse_args()
    ruta = Path(args.instancia)
    if not ruta.is_file():
        # Permite escribir solo berlin52.tsp o ta001.txt desde la raíz del proyecto.
        ruta = next((candidata for candidata in (RAIZ / "data" / ruta, RAIZ / "berlin52" / ruta) if candidata.is_file()), ruta)
    if not ruta.is_file():
        crear_parser().error(f"No se encontró la instancia: {args.instancia}")

    inicio = time.perf_counter()
    if ruta.suffix.lower() == ".tsp":
        # Berlin52 es TSP: la función objetivo es distancia de tour, no C_max.
        instancia_tsp = leer_berlin52(ruta)
        permutacion, costo, historia = ejecutar_acs_berlin52(
            instancia_tsp.datos, args.hormigas, args.iteraciones, args.alpha,
            args.beta, args.q0, args.semilla, True,
        )
        instancia, mejor_conocido, etiqueta = instancia_tsp.nombre, instancia_tsp.metadatos.get("mejor_conocido"), "distancia"
    else:
        instancia_pfsp = leer_instancia_taillard(ruta)
        permutacion, costo, historia = ejecutar_acs(
        instancia_pfsp.datos, args.hormigas, args.iteraciones, args.alpha,
            args.beta, args.q0, args.semilla, True,
        )
        instancia, mejor_conocido, etiqueta = instancia_pfsp.nombre, instancia_pfsp.metadatos.get("mejor_conocido"), "C_max"

    fila = guardar_resultado(RAIZ / args.salida, "ACS", instancia, costo, permutacion,
                            mejor_conocido, time.perf_counter() - inicio, etiqueta)
    print(f"ACS | {instancia} | {etiqueta}={costo:.2f} | RPD={fila['rpd_porcentaje']}%")
    print(f"Resultado: {RAIZ / args.salida}")
    return historia


if __name__ == "__main__":
    main()
