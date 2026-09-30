import os
import sys
import argparse
import numpy as np


def window_path(path, directory):
    ruta = os.path.expanduser(path)
    if os.path.isabs(ruta):
        return os.path.normpath(path)

    script_directory = os.path.dirname(os.path.abspath(__file__))
    if sys.platform == "win32":
        relative_path = directory + "\\" + ruta
    else:
        relative_path = directory + "/" + ruta

    return os.path.normpath(os.path.join(script_directory, relative_path))


def createParser():
    parser = argparse.ArgumentParser(
        description="Ejecuta el algoritmo ACS (Ant Colony System) con los parametros indicados.",
        epilog=(
            "Ejemplo: python acs.py instancia.txt 50 200 1.0 2.0 0.9 12345 resultados.csv"
        ),
    )
    # 1. Archivo de entrada
    parser.add_argument(
        "entrada",
        help="Nombre del archivo de entrada dentro de data/.",
    )
    # 2. Número de hormigas
    parser.add_argument(
        "num_hormigas",
        type=int,
        help="Numero de hormigas.",
    )
    # 3. Número de iteraciones
    parser.add_argument(
        "num_ite",
        type=int,
        help="Cantidad de iteraciones del algoritmo.",
    )
    # 4. Parámetros propios de ACS (alpha, beta, rho/evaporacion)
    parser.add_argument(
        "alpha",
        type=float,
        help="Peso relativo de la feromona (alpha).",
    )
    parser.add_argument(
        "beta",
        type=float,
        help="Peso relativo de la heuristica (beta).",
    )
    parser.add_argument(
        "evaporacion",
        type=float,
        help="Tasa de evaporacion de feromona (rho), entre 0 y 1.",
    )
    # 5. Semilla aleatoria
    parser.add_argument(
        "semilla",
        type=int,
        help="Semilla del generador aleatorio.",
    )
    # 6. Archivo de salida
    parser.add_argument(
        "salida",
        help="Nombre del archivo de salida dentro de result/.",
    )
    return parser

def main():
    args = createParser().parse_args()
    entrada = window_path(args.entrada, "data")
    num_hormigas = args.num_hormigas
    num_ite = args.num_ite
    alpha = args.alpha
    beta = args.beta
    evaporacion = args.evaporacion
    semilla = args.semilla
    salida = window_path(args.salida, "result")


    if not os.path.isfile(entrada):
        createParser().error(
            f"No se encontro el archivo de entrada: {entrada}"
        )

    os.makedirs(os.path.dirname(salida), exist_ok=True)
    with open(entrada, "r", encoding="utf-8") as f:
        f.readline()
        metadatos = f.readline().split("#", 1)[1].split()
        f.readline()
        data_info = f.readline().strip().split()
        num_job = int(data_info[0])
        num_maquinas = int(data_info[1])
        seed = int(metadatos[2])
        lim_inf = int(metadatos[3])
        lim_sup = int(metadatos[4])
        matriz = np.loadtxt(f, dtype=int)
    print(f"P1: {num_job},P2: {num_maquinas} P3: {seed}, lim_inf: {lim_inf}, lim_sup: {lim_sup}")
    print(f"Datos de hormigas de parametros: numero hormigas {num_hormigas} ,numero iteraciones {num_ite}, alpha {alpha}, beta {beta}, evaporacion {evaporacion}, semilla {semilla}, archivo salida {salida}-")
    print(matriz)


    

if __name__ == '__main__':
    main()