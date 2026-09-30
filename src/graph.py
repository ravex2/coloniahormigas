import os
import sys
import csv
import matplotlib.pyplot as plt
import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

def graficar_comparacion_rpd(csv_path=None, output_path=None):
    """Lee el CSV de benchmark y genera un grafico de barras comparando el RPD(%) de AG vs Memetico."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)

    if csv_path is None:
        csv_path = os.path.join(project_dir, "result", "benchmark_results.csv")
    if output_path is None:
        output_path = os.path.join(project_dir, "result", "comparativa_ag_vs_memetico.png")

    if not os.path.isfile(csv_path):
        print(f"Error: No se encontro el archivo CSV en {csv_path}")
        return

    instancias = []
    rpd_ag = []
    rpd_mem = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tag = f"{row['Instancia']}\n({row['Trabajos']}x{row['Maquinas']})"
            instancias.append(tag)
            rpd_ag.append(float(row['RPD_AG']))
            rpd_mem.append(float(row['RPD_Memetico']))

    x = np.arange(len(instancias))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))

    rects1 = ax.bar(x - width/2, rpd_ag, width, label='AG Puro', color='#3498db')
    rects2 = ax.bar(x + width/2, rpd_mem, width, label='Algoritmo Memético', color='#e74c3c')

    ax.set_ylabel('RPD (%) (Menor es mejor)', fontsize=12)
    ax.set_title('Comparativa RPD (%): AG Puro vs. Algoritmo Memético en Instancias de Taillard', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(instancias, fontsize=9, rotation=15)
    ax.legend(fontsize=11)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Añadir valores sobre las barras
    ax.bar_label(rects1, padding=3, fmt='%.1f%%', fontsize=8)
    ax.bar_label(rects2, padding=3, fmt='%.1f%%', fontsize=8)

    fig.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Gráfica comparativa guardada en: {output_path}")

def graficar_boxplot_rpd(csv_path=None, output_path=None):
    """Genera un grafico de diagramas de caja (Box Plot) comparando la distribucion de RPD (%) del AG Puro vs. Memetico."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)

    if csv_path is None:
        csv_path = os.path.join(project_dir, "result", "benchmark_results.csv")
    if output_path is None:
        output_path = os.path.join(project_dir, "result", "boxplot_rpd.png")

    if not os.path.isfile(csv_path):
        print(f"Error: No se encontro el archivo CSV en {csv_path}")
        return

    rpd_ag = []
    rpd_mem = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rpd_ag.append(float(row['RPD_AG']))
            rpd_mem.append(float(row['RPD_Memetico']))

    fig, ax = plt.subplots(figsize=(8, 6))

    datos = [rpd_ag, rpd_mem]
    etiquetas = ['AG Puro', 'Algoritmo Memético']

    bp = ax.boxplot(datos, patch_artist=True, tick_labels=etiquetas,
                    boxprops=dict(alpha=0.7, linewidth=1.5),
                    medianprops=dict(color='black', linewidth=2),
                    whiskerprops=dict(linewidth=1.5),
                    capprops=dict(linewidth=1.5),
                    showmeans=True,
                    meanprops=dict(marker='D', markeredgecolor='black', markerfacecolor='yellow'))

    colores = ['#3498db', '#e74c3c']
    for patch, color in zip(bp['boxes'], colores):
        patch.set_facecolor(color)

    # Añadir puntos de datos individuales con leve dispersión (jitter)
    for i, data in enumerate(datos):
        x = np.random.normal(i + 1, 0.04, size=len(data))
        ax.plot(x, data, 'o', color='black', alpha=0.6, markersize=5)

    ax.set_ylabel('RPD (%) (Menor es mejor)', fontsize=12)
    ax.set_title('Distribución General de RPD (%): AG Puro vs. Algoritmo Memético', fontsize=14, fontweight='bold')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    fig.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Gráfica Box Plot guardada en: {output_path}")


def graficar_boxplot_maskepan(csv_path=None, output_path=None):
    """Genera un grafico de diagramas de caja (Box Plot) comparando la distribucion de maskepan del AG Puro vs. Memetico."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)

    if csv_path is None:
        csv_path = os.path.join(project_dir, "result", "benchmark_results.csv")
    if output_path is None:
        output_path = os.path.join(project_dir, "result", "boxplot_maskepan.png")

    if not os.path.isfile(csv_path):
        print(f"Error: No se encontro el archivo CSV en {csv_path}")
        return

    rpd_ag = []
    rpd_mem = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rpd_ag.append(float(row['Makespan_AG']))
            rpd_mem.append(float(row['Makespan_Memetico']))

    fig, ax = plt.subplots(figsize=(8, 6))

    datos = [rpd_ag, rpd_mem]
    etiquetas = ['AG', 'Algoritmo Memético']

    bp = ax.boxplot(datos, patch_artist=True, tick_labels=etiquetas,
                    boxprops=dict(alpha=0.7, linewidth=1.5),
                    medianprops=dict(color='black', linewidth=2),
                    whiskerprops=dict(linewidth=1.5),
                    capprops=dict(linewidth=1.5),
                    showmeans=True,
                    meanprops=dict(marker='D', markeredgecolor='black', markerfacecolor='yellow'))

    colores = ['#3498db', '#e74c3c']
    for patch, color in zip(bp['boxes'], colores):
        patch.set_facecolor(color)

    # Añadir puntos de datos individuales con leve dispersión (jitter)
    for i, data in enumerate(datos):
        x = np.random.normal(i + 1, 0.04, size=len(data))
        ax.plot(x, data, 'o', color='black', alpha=0.6, markersize=5)

    ax.set_ylabel('RPD (%) (Menor es mejor)', fontsize=12)
    ax.set_title('Distribución General Maskepan: AG vs. Algoritmo Memético', fontsize=14, fontweight='bold')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    fig.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Gráfica Box Plot guardada en: {output_path}")


def graficar_boxplot_ejecuciones_instancia(nombre_instancia="ta041.txt", num_ejecuciones=20, output_path=None):
    """Ejecuta N carreras independientes con semillas distintas sobre una instancia y grafica el Box Plot de los RPDs."""
    from src.ag_build import ejecutar_algoritmo_genetico, ejecutar_algoritmo_memetico
    from script.run_benchmark import leer_instancia_taillard

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_path = os.path.join(project_dir, "data", nombre_instancia)

    if output_path is None:
        output_path = os.path.join(project_dir, "result", f"boxplot_ejecuciones_{nombre_instancia.replace('.txt', '')}.png")

    if not os.path.isfile(data_path):
        print(f"Error: No se encontró el archivo de datos {data_path}")
        return

    _, _, upper_bound, tiempos = leer_instancia_taillard(data_path)

    rpds_ag = []
    rpds_mem = []

    print(f"Ejecutando {num_ejecuciones} ejecuciones independientes para {nombre_instancia}...")
    for semilla in range(1, num_ejecuciones + 1):
        _, mk_ag = ejecutar_algoritmo_genetico(
            tiempos, tam_pob=30, por_cru=0.8, por_mul=0.1, num_ite=100, semilla=semilla
        )
        _, mk_mem = ejecutar_algoritmo_memetico(
            tiempos, tam_pob=30, por_cru=0.8, por_mul=0.1, num_ite=100, semilla=semilla, frecuencia_local=1
        )
        rpds_ag.append(((mk_ag - upper_bound) / upper_bound) * 100.0)
        rpds_mem.append(((mk_mem - upper_bound) / upper_bound) * 100.0)

    fig, ax = plt.subplots(figsize=(8, 6))

    datos = [rpds_ag, rpds_mem]
    etiquetas = ['AG Puro', 'Algoritmo Memético']

    bp = ax.boxplot(datos, patch_artist=True, tick_labels=etiquetas,
                    boxprops=dict(alpha=0.7, linewidth=1.5),
                    medianprops=dict(color='black', linewidth=2),
                    showmeans=True,
                    meanprops=dict(marker='D', markeredgecolor='black', markerfacecolor='yellow'))

    colores = ['#3498db', '#e74c3c']
    for patch, color in zip(bp['boxes'], colores):
        patch.set_facecolor(color)

    # Añadir puntos de datos individuales
    for i, data in enumerate(datos):
        x = np.random.normal(i + 1, 0.04, size=len(data))
        ax.plot(x, data, 'o', color='black', alpha=0.6, markersize=5)

    ax.set_ylabel('RPD (%) (Menor es mejor)', fontsize=12)
    ax.set_title(f'Variabilidad de RPD en {num_ejecuciones} Ejecuciones ({nombre_instancia})', fontsize=14, fontweight='bold')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    fig.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Gráfica Box Plot por ejecuciones guardada en: {output_path}")

def graficar_convergencia_instancia(nombre_instancia="ta001.txt", num_ite=100, output_path=None):
    """Grafica la curva de convergencia (Generaciones vs Makespan) para una instancia dada."""
    from src.ag_build import ejecutar_algoritmo_genetico, ejecutar_algoritmo_memetico
    from script.run_benchmark import leer_instancia_taillard

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_path = os.path.join(project_dir, "data", nombre_instancia)

    if output_path is None:
        output_path = os.path.join(project_dir, "result", f"convergencia_{nombre_instancia.replace('.txt', '')}.png")

    if not os.path.isfile(data_path):
        print(f"Error: No se encontró el archivo de datos {data_path}")
        return

    _, _, upper_bound, tiempos = leer_instancia_taillard(data_path)

    _, _, hist_ag = ejecutar_algoritmo_genetico(
        tiempos, tam_pob=30, por_cru=0.8, por_mul=0.1, num_ite=num_ite, semilla=42, retornar_historia=True
    )
    _, _, hist_mem = ejecutar_algoritmo_memetico(
        tiempos, tam_pob=30, por_cru=0.8, por_mul=0.1, num_ite=num_ite, semilla=42, frecuencia_local=1, retornar_historia=True
    )

    plt.figure(figsize=(10, 5))
    plt.plot(hist_ag, label='AG Puro', color='#3498db', linewidth=2)
    plt.plot(hist_mem, label='Algoritmo Memético', color='#e74c3c', linewidth=2)
    plt.axhline(y=upper_bound, color='green', linestyle='--', label=f'Óptimo / Upper Bound ({upper_bound})')

    plt.xlabel('Generación', fontsize=12)
    plt.ylabel('Makespan (Cmax)', fontsize=12)
    plt.title(f'Curva de Convergencia en {nombre_instancia}', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Gráfica de convergencia guardada en: {output_path}")

if __name__ == "__main__":
    graficar_comparacion_rpd()
    graficar_boxplot_rpd()
    graficar_boxplot_maskepan()
    graficar_boxplot_ejecuciones_instancia("ta041.txt", num_ejecuciones=15)