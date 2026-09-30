import sys
import os 
import argparse
import random
import numpy as np
from src.pfsp import fitness_pfsp
from src.ag_build import ejecutar_algoritmo_memetico

def resolve_path_windows(path, directory):
    ruta = os.path.expanduser(path)
    if os.path.isabs(ruta):
        return os.path.normpath(path)

    script_directory = os.path.dirname(os.path.abspath(__file__))
    if sys.platform == "win32":
        relative_path = directory + "\\" + ruta
    else:
        relative_path = directory + "/" + ruta

    return os.path.normpath(os.path.join(script_directory, relative_path))

def lsDirectory(directory):
    files = []
    for filename in os.listdir(directory):
        ruta_archivo = os.path.join(directory, filename)
        if os.path.isfile(ruta_archivo):
            files.append(filename)
    return files


def createParser():
    parser = argparse.ArgumentParser(
        description="Ejecuta el algoritmo genetico con los parametros indicados.",
        epilog=(
            "Ejemplo: python3 ag.py 42 100 0.8 0.1 500 entrada.txt salida.txt"
        ),
    )
    parser.add_argument("semilla", type=int, help="Semilla del generador aleatorio.")
    parser.add_argument(
        "tam_pob",
        type=int,
        help="Tamano de la poblacion inicial.",
    )
    parser.add_argument(
        "por_cru",
        type=float,
        help="Probabilidad de cruce, entre 0 y 1.",
    )
    parser.add_argument(
        "por_mul",
        type=float,
        help="Probabilidad de mutacion, entre 0 y 1.",
    )
    parser.add_argument(
        "num_ite",
        type=int,
        help="Cantidad de iteraciones del algoritmo.",
    )
    parser.add_argument(
        "entrada",
        help="Nombre del archivo de entrada dentro de data/.",
    )
    parser.add_argument(
        "salida",
        help="Nombre del archivo de salida dentro de result/.",
    )
    parser.add_argument("gene", type=int, default=1,
                        help="Aplicar busqueda local cada N generaciones (por defecto 1).")
    return parser


def saveData(salida, cantidad_trabajos, cantidad_maquinas, makespan, mejor):
    with open(salida, "w", encoding="utf-8") as archivo:
        archivo.write(f"Trabajos: {cantidad_trabajos}\n")
        archivo.write(f"Maquinas: {cantidad_maquinas}\n")
        archivo.write(f"Makespan: {makespan}\n")
        archivo.write(
            "Permutacion: " + " ".join(str(trabajo + 1) for trabajo in mejor) + "\n"
        )

    print(f"Makespan: {makespan}")
    print(f"Resultado guardado en: {salida}")


def main():
    #files = lsDirectory("data")
    #print("Archivos de entrada disponibles en data/: ", files)
    
    #if not files:
    #    createParser().error("No se encontraron archivos de entrada en el directorio data/.")
    
    args = createParser().parse_args()
    semilla = args.semilla
    tam_pob = args.tam_pob
    por_cru = args.por_cru
    por_mul = args.por_mul
    num_ite = args.num_ite
    generacion = args.gene
    entrada = resolve_path_windows(args.entrada, "data")
    salida = resolve_path_windows(args.salida, "result")

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
    print(matriz)

    mejor, makespan = ejecutar_algoritmo_memetico(
        matriz,
        args.tam_pob,
        args.por_cru,
        args.por_mul,
        args.num_ite,
        args.semilla,
        args.gene
    )

    print("Maskepan: ", makespan)
    print("Mejores: ", mejor)
    saveData(salida, num_job, num_maquinas, makespan, mejor)




if __name__ == "__main__":
    main()
