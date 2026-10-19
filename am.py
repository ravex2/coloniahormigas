"""Punto de entrada independiente para el Algoritmo Memético (AM)."""

import argparse
import time
from pathlib import Path

from src.am_build import ejecutar_algoritmo_memetico
from src.operadores import leer_instancia_taillard
from src.salidas import guardar_resultado

RAIZ = Path(__file__).resolve().parent


def crear_parser():
    parser = argparse.ArgumentParser(description="Resuelve una instancia PFSP mediante Algoritmo Memético.")
    parser.add_argument("instancia", help="Archivo Taillard (nombre en data/ o ruta).")
    parser.add_argument("--poblacion", type=int, default=40)
    parser.add_argument("--iteraciones", type=int, default=200)
    parser.add_argument("--cruce", type=float, default=0.9)
    parser.add_argument("--mutacion", type=float, default=0.15)
    parser.add_argument("--frecuencia-local", type=int, default=5)
    parser.add_argument("--evaluaciones-locales", type=int, default=1000)
    parser.add_argument("--semilla", type=int, default=42)
    parser.add_argument("--salida", default="resultados/am.csv")
    return parser


def main():
    args = crear_parser().parse_args()
    ruta = Path(args.instancia)
    instancia = leer_instancia_taillard(ruta if ruta.is_file() else RAIZ / "data" / ruta)
    inicio = time.perf_counter()
    permutacion, makespan, historia = ejecutar_algoritmo_memetico(
        instancia.datos, args.poblacion, args.cruce, args.mutacion, args.iteraciones, args.semilla,
        args.frecuencia_local, args.evaluaciones_locales, True,
    )
    fila = guardar_resultado(RAIZ / args.salida, "AM", instancia.nombre, makespan, permutacion,
                            instancia.metadatos.get("mejor_conocido"), time.perf_counter() - inicio)
    print(f"AM | {instancia.nombre} | C_max={makespan} | RPD={fila['rpd_porcentaje']}%")
    print(f"Resultado: {RAIZ / args.salida}")
    return historia


if __name__ == "__main__":
    main()
