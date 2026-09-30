import os
import sys
import time
import csv
import numpy as np

# Agregar directorio raiz del proyecto al path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
sys.path.insert(0, project_dir)

from src.ag_build import ejecutar_algoritmo_genetico, ejecutar_algoritmo_memetico

def leer_instancia_taillard(path_archivo):
    """Lee un archivo de Taillard y extrae num_jobs, num_maquinas, upper_bound y la matriz de tiempos."""
    with open(path_archivo, "r", encoding="utf-8") as f:
        f.readline()  # Comentario de cabecera 1
        metadatos = f.readline().split("#", 1)[1].split()
        f.readline()  # Comentario de cabecera 2
        data_info = f.readline().strip().split()
        
        num_jobs = int(data_info[0])
        num_maquinas = int(data_info[1])
        upper_bound = int(metadatos[3])
        
        matriz = np.loadtxt(f, dtype=int)
        
    return num_jobs, num_maquinas, upper_bound, matriz

def ejecutar_benchmark(instancias=None, semilla=42, tam_pob=30, por_cru=0.8, por_mul=0.1, num_ite=100):
    if instancias is None:
        # Selección representativa de instancias de distintos tamaños
        instancias = [
            "ta001.txt", "ta002.txt",  # 20x5
            "ta011.txt", "ta012.txt",  # 20x10
            "ta021.txt", "ta022.txt",  # 20x20
            "ta031.txt", "ta032.txt",  # 50x5
            "ta041.txt", "ta042.txt",  # 50x10
            "ta051.txt", "ta052.txt"   # 50x20
        ]

    data_dir = os.path.join(project_dir, "data")
    result_dir = os.path.join(project_dir, "result")
    os.makedirs(result_dir, exist_ok=True)
    csv_salida = os.path.join(result_dir, "benchmark_results.csv")

    resultados = []

    print("=" * 80)
    print("EJECUTANDO BENCHMARK: AG PURO vs ALGORITMO MEMETICO")
    print("=" * 80)

    for nombre_instancia in instancias:
        path_instancia = os.path.join(data_dir, nombre_instancia)
        if not os.path.isfile(path_instancia):
            print(f"Instancia no encontrada: {nombre_instancia}, omitiendo...")
            continue

        num_jobs, num_maquinas, upper_bound, tiempos = leer_instancia_taillard(path_instancia)
        instancia_tag = f"{nombre_instancia} ({num_jobs}x{num_maquinas})"
        print(f"\nProcesando {instancia_tag} | Upper Bound: {upper_bound}")

        # --- 1. AG PURO ---
        t0 = time.time()
        _, makespan_ag = ejecutar_algoritmo_genetico(
            tiempos, tam_pob, por_cru, por_mul, num_ite, semilla
        )
        t_ag = time.time() - t0
        rpd_ag = ((makespan_ag - upper_bound) / upper_bound) * 100.0

        # --- 2. ALGORITMO MEMETICO ---
        t0 = time.time()
        _, makespan_mem = ejecutar_algoritmo_memetico(
            tiempos, tam_pob, por_cru, por_mul, num_ite, semilla, frecuencia_local=1
        )
        t_mem = time.time() - t0
        rpd_mem = ((makespan_mem - upper_bound) / upper_bound) * 100.0

        print(f"  [AG Puro]    Makespan: {makespan_ag} | RPD: {rpd_ag:.2f}% | Tiempo: {t_ag:.2f}s")
        print(f"  [Memético]  Makespan: {makespan_mem} | RPD: {rpd_mem:.2f}% | Tiempo: {t_mem:.2f}s")

        resultados.append({
            "Instancia": nombre_instancia,
            "Trabajos": num_jobs,
            "Maquinas": num_maquinas,
            "UpperBound": upper_bound,
            "Makespan_AG": makespan_ag,
            "RPD_AG": round(rpd_ag, 2),
            "Tiempo_AG": round(t_ag, 3),
            "Makespan_Memetico": makespan_mem,
            "RPD_Memetico": round(rpd_mem, 2),
            "Tiempo_Memetico": round(t_mem, 3),
        })

    # Guardar a CSV
    columnas = [
        "Instancia", "Trabajos", "Maquinas", "UpperBound",
        "Makespan_AG", "RPD_AG", "Tiempo_AG",
        "Makespan_Memetico", "RPD_Memetico", "Tiempo_Memetico"
    ]
    
    with open(csv_salida, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columnas)
        writer.writeheader()
        writer.writerows(resultados)

    print("\n" + "=" * 80)
    print(f"Benchmark finalizado. Resultados guardados en: {csv_salida}")
    print("=" * 80)
    return csv_salida

if __name__ == "__main__":
    ejecutar_benchmark()
