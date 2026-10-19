"""Orquestador para comparar AG, AM y ACS en una misma instancia PFSP."""

import argparse
import csv
import time
from pathlib import Path

from src.acs_build import ejecutar_acs
from src.ag_build import ejecutar_algoritmo_genetico
from src.am_build import ejecutar_algoritmo_memetico
from src.graficos import guardar_convergencia
from src.operadores import leer_instancia_taillard
from src.salidas import guardar_resultado

RAIZ = Path(__file__).resolve().parent


def crear_parser():
    parser = argparse.ArgumentParser(description="Compara AG, AM y ACS para una instancia Taillard de PFSP.")
    parser.add_argument("instancia", help="Nombre en data/ o ruta al archivo Taillard.")
    parser.add_argument("--iteraciones", type=int, default=200)
    parser.add_argument("--poblacion", type=int, default=40)
    parser.add_argument("--hormigas", type=int, default=30)
    parser.add_argument("--semilla", type=int, default=42)
    parser.add_argument("--salida", default="resultados/comparacion.csv")
    parser.add_argument("--grafico", action="store_true", help="Genera un PNG de convergencia en graficos/.")
    return parser


def ejecutar(nombre, funcion):
    inicio = time.perf_counter()
    permutacion, makespan, historia = funcion()
    return nombre, permutacion, makespan, historia, time.perf_counter() - inicio


def main():
    args = crear_parser().parse_args()
    ruta = Path(args.instancia)
    instancia = leer_instancia_taillard(ruta if ruta.is_file() else RAIZ / "data" / ruta)
    comun = (instancia.datos, args.poblacion, 0.9, 0.15, args.iteraciones, args.semilla)
    corridas = [
        ejecutar("AG", lambda: ejecutar_algoritmo_genetico(*comun, retornar_historia=True)),
        ejecutar("AM", lambda: ejecutar_algoritmo_memetico(*comun, frecuencia_local=5, retornar_historia=True)),
        ejecutar("ACS", lambda: ejecutar_acs(instancia.datos, args.hormigas, args.iteraciones, 0.1, 2.0, 0.8, args.semilla, True)),
    ]
    salida = RAIZ / args.salida
    salida.parent.mkdir(parents=True, exist_ok=True)
    filas = []
    for algoritmo, permutacion, makespan, _, segundos in corridas:
        filas.append(guardar_resultado(salida.parent / f"{algoritmo.lower()}_ultimo.csv", algoritmo, instancia.nombre,
                                      makespan, permutacion, instancia.metadatos.get("mejor_conocido"), segundos))
    with salida.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=filas[0].keys())
        escritor.writeheader()
        escritor.writerows(filas)
    for fila in filas:
        print(f"{fila['algoritmo']}: C_max={fila['makespan']} | RPD={fila['rpd_porcentaje']}% | {fila['segundos']} s")
    print(f"Comparación: {salida}")
    if args.grafico:
        ruta_grafico = guardar_convergencia(
            {nombre: historia for nombre, _, _, historia, _ in corridas},
            RAIZ / "graficos" / f"convergencia_{instancia.nombre}.png",
        )
        print(f"Gráfico: {ruta_grafico}")
    return filas


if __name__ == "__main__":
    main()
