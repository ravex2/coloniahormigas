"""Gráficos comparativos reproducibles para AG, AM y ACS."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.acs_build import ejecutar_acs
from src.ag_build import ejecutar_algoritmo_genetico
from src.am_build import ejecutar_algoritmo_memetico
from src.operadores import leer_instancia_taillard

ALGORITMOS = (("AG", "#3498db"), ("AM", "#e74c3c"), ("ACS", "#2ca02c"))


def _guardar(figura, ruta):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    figura.tight_layout()
    figura.savefig(ruta, dpi=200)
    plt.close(figura)
    print(f"Gráfico guardado en: {ruta}")
    return ruta


def guardar_convergencia(historiales, ruta, titulo="Convergencia de metaheurísticas PFSP"):
    """Guarda una curva por algoritmo a partir de su historial de mejor C_max."""
    figura, eje = plt.subplots(figsize=(10, 5))
    colores = dict(ALGORITMOS)
    for nombre, historia in historiales.items():
        # AG/AM incluyen el estado inicial (0); ACS empieza tras su iteración 1.
        inicio = 1 if nombre == "ACS" else 0
        eje.plot(np.arange(inicio, inicio + len(historia)), historia, label=nombre, color=colores.get(nombre), linewidth=2)
    eje.set(title=titulo, xlabel="Iteración", ylabel="Mejor C_max")
    eje.legend()
    eje.grid(alpha=0.3)
    return _guardar(figura, ruta)


def _leer_benchmark(ruta):
    with Path(ruta).open(encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    requeridas = {f"RPD_{nombre}" for nombre, _ in ALGORITMOS}
    if not filas or not requeridas.issubset(filas[0]):
        raise ValueError("El CSV debe contener resultados RPD de AG, AM y ACS. Ejecute primero run_benchmark.py.")
    return filas


def graficar_comparacion_rpd(csv_path=None, output_path=None):
    """Barras de RPD por instancia para los tres algoritmos."""
    filas = _leer_benchmark(csv_path or RAIZ / "resultados" / "benchmark_results.csv")
    etiquetas = [f"{fila['Instancia']}\n({fila['Trabajos']}x{fila['Maquinas']})" for fila in filas]
    x, ancho = np.arange(len(filas)), 0.24
    figura, eje = plt.subplots(figsize=(max(10, len(filas) * 0.9), 6))
    for indice, (nombre, color) in enumerate(ALGORITMOS):
        valores = [float(fila[f"RPD_{nombre}"]) for fila in filas]
        barras = eje.bar(x + (indice - 1) * ancho, valores, ancho, label=nombre, color=color)
        eje.bar_label(barras, padding=2, fmt="%.1f", fontsize=7)
    eje.set(title="Comparación de RPD: AG, AM y ACS", ylabel="RPD (%) - menor es mejor")
    eje.set_xticks(x, etiquetas, rotation=15, ha="right")
    eje.legend()
    eje.grid(axis="y", alpha=0.3)
    return _guardar(figura, output_path or RAIZ / "graficos" / "comparativa_rpd.png")


def graficar_boxplot_rpd(csv_path=None, output_path=None):
    """Box plot de RPD de AG, AM y ACS para las instancias del benchmark."""
    filas = _leer_benchmark(csv_path or RAIZ / "resultados" / "benchmark_results.csv")
    datos = [[float(fila[f"RPD_{nombre}"]) for fila in filas] for nombre, _ in ALGORITMOS]
    figura, eje = plt.subplots(figsize=(8, 5))
    cajas = eje.boxplot(datos, patch_artist=True, tick_labels=[nombre for nombre, _ in ALGORITMOS], showmeans=True)
    for caja, (_, color) in zip(cajas["boxes"], ALGORITMOS):
        caja.set_facecolor(color)
    eje.set(title="Distribución de RPD", ylabel="RPD (%) - menor es mejor")
    eje.grid(axis="y", alpha=0.3)
    return _guardar(figura, output_path or RAIZ / "graficos" / "boxplot_rpd.png")


def graficar_boxplot_makespan(csv_path=None, output_path=None):
    """Box plot de makespan de AG, AM y ACS para las instancias del benchmark."""
    filas = _leer_benchmark(csv_path or RAIZ / "resultados" / "benchmark_results.csv")
    datos = [[float(fila[f"Makespan_{nombre}"]) for fila in filas] for nombre, _ in ALGORITMOS]
    figura, eje = plt.subplots(figsize=(8, 5))
    cajas = eje.boxplot(datos, patch_artist=True, tick_labels=[nombre for nombre, _ in ALGORITMOS], showmeans=True)
    for caja, (_, color) in zip(cajas["boxes"], ALGORITMOS):
        caja.set_facecolor(color)
    eje.set(title="Distribución de makespan", ylabel="C_max - menor es mejor")
    eje.grid(axis="y", alpha=0.3)
    return _guardar(figura, output_path or RAIZ / "graficos" / "boxplot_makespan.png")


def _ejecutar_tres(tiempos, iteraciones, semilla):
    return {
        "AG": ejecutar_algoritmo_genetico(tiempos, 30, 0.9, 0.15, iteraciones, semilla, retornar_historia=True),
        "AM": ejecutar_algoritmo_memetico(tiempos, 30, 0.9, 0.15, iteraciones, semilla, frecuencia_local=5, retornar_historia=True),
        "ACS": ejecutar_acs(tiempos, 30, iteraciones, 0.1, 2.0, 0.8, semilla, retornar_historia=True),
    }


def graficar_boxplot_ejecuciones_instancia(nombre_instancia="ta001.txt", num_ejecuciones=20, iteraciones=100, output_path=None):
    """Mide la variabilidad de AG, AM y ACS en múltiples semillas."""
    instancia = leer_instancia_taillard(RAIZ / "data" / nombre_instancia)
    resultados = {nombre: [] for nombre, _ in ALGORITMOS}
    for semilla in range(1, num_ejecuciones + 1):
        for nombre, (_, makespan, _) in _ejecutar_tres(instancia.datos, iteraciones, semilla).items():
            mejor = instancia.metadatos["mejor_conocido"]
            resultados[nombre].append((makespan - mejor) * 100 / mejor)
    figura, eje = plt.subplots(figsize=(8, 5))
    cajas = eje.boxplot([resultados[nombre] for nombre, _ in ALGORITMOS], patch_artist=True,
                         tick_labels=[nombre for nombre, _ in ALGORITMOS], showmeans=True)
    for caja, (_, color) in zip(cajas["boxes"], ALGORITMOS):
        caja.set_facecolor(color)
    eje.set(title=f"RPD en {num_ejecuciones} ejecuciones: {nombre_instancia}", ylabel="RPD (%)")
    eje.grid(axis="y", alpha=0.3)
    return _guardar(figura, output_path or RAIZ / "graficos" / f"boxplot_{Path(nombre_instancia).stem}.png")


def graficar_convergencia_instancia(nombre_instancia="ta001.txt", num_ite=100, output_path=None):
    """Grafica la convergencia de AG, AM y ACS sobre una misma instancia."""
    instancia = leer_instancia_taillard(RAIZ / "data" / nombre_instancia)
    resultados = _ejecutar_tres(instancia.datos, num_ite, 42)
    figura, eje = plt.subplots(figsize=(10, 5))
    for nombre, color in ALGORITMOS:
        historia = resultados[nombre][2]
        inicio = 1 if nombre == "ACS" else 0
        eje.plot(np.arange(inicio, inicio + len(historia)), historia, label=nombre, color=color, linewidth=2)
    mejor = instancia.metadatos.get("mejor_conocido")
    if mejor is not None:
        eje.axhline(mejor, color="black", linestyle="--", label=f"Mejor conocido ({mejor})")
    eje.set(title=f"Convergencia: AG, AM y ACS en {nombre_instancia}", xlabel="Iteración", ylabel="Mejor C_max")
    eje.legend()
    eje.grid(alpha=0.3)
    return _guardar(figura, output_path or RAIZ / "graficos" / f"convergencia_{Path(nombre_instancia).stem}.png")


def graficar_convergencia_acs(nombre_instancia="ta001.txt", iteraciones=100):
    """Ejecuta únicamente ACS PFSP y guarda su evolución real de C_max."""
    instancia = leer_instancia_taillard(RAIZ / "data" / nombre_instancia)
    _, _, historia = ejecutar_acs(instancia.datos, 30, iteraciones, .1, 2, .8, 42, retornar_historia=True)
    return guardar_convergencia({"ACS": historia},
        RAIZ / "graficos" / f"acs_convergencia_{Path(nombre_instancia).stem}.png",
        titulo=f"ACS PFSP · {nombre_instancia}")


def graficar_benchmark_por_tamano(csv_path=None):
    """Separa escalas: cada columna corresponde a un tamaño de Taillard.

    Las cajas describen variación entre instancias, no repeticiones de semillas.
    Cada fila muestra una métrica: calidad absoluta, relativa y costo temporal.
    """
    tabla = pd.DataFrame(_leer_benchmark(csv_path or RAIZ / 'resultados/benchmark_results.csv'))
    tamanos = [(20, 5), (50, 10), (100, 10)]
    figura, ejes = plt.subplots(3, 3, figsize=(15, 11))
    for col, (trabajos, maquinas) in enumerate(tamanos):
        grupo = tabla[(tabla.Trabajos.astype(int) == trabajos) & (tabla.Maquinas.astype(int) == maquinas)]
        for fila, (metrica, etiqueta) in enumerate([('Makespan', 'C_max'), ('RPD', 'RPD (%)'), ('Tiempo', 'Segundos')]):
            eje = ejes[fila, col]
            eje.set_title(f'{trabajos}×{maquinas} · {len(grupo)} instancias')
            eje.set_ylabel(etiqueta)
            if grupo.empty:
                eje.text(.5, .5, 'Sin resultados', ha='center', transform=eje.transAxes)
                continue
            datos = [grupo[f'{metrica}_{nombre}'].astype(float).to_numpy() for nombre, _ in ALGORITMOS]
            cajas = eje.boxplot(datos, tick_labels=[n for n, _ in ALGORITMOS], patch_artist=True, showmeans=True)
            for caja, (_, color) in zip(cajas['boxes'], ALGORITMOS):
                caja.set_facecolor(color)
            eje.grid(axis='y', alpha=.25)
    return _guardar(figura, RAIZ / 'graficos/benchmark_por_tamano.png')


def main():
    parser = argparse.ArgumentParser(description="Genera gráficos comparativos de AG, AM y ACS.")
    parser.add_argument("--instancia", default="ta001.txt")
    parser.add_argument("--iteraciones", type=int, default=100)
    parser.add_argument("--ejecuciones", type=int, default=20)
    parser.add_argument("--benchmark", action="store_true", help="Genera gráficos desde resultados/benchmark_results.csv.")
    parser.add_argument("--acs", action="store_true", help="Genera únicamente la convergencia de ACS PFSP.")
    parser.add_argument("--csv", help="CSV del benchmark a graficar.")
    args = parser.parse_args()
    if args.benchmark:
        graficar_comparacion_rpd(args.csv)
        graficar_boxplot_rpd(args.csv)
        graficar_benchmark_por_tamano(args.csv)
    elif args.acs:
        graficar_convergencia_acs(args.instancia, args.iteraciones)
    else:
        graficar_convergencia_instancia(args.instancia, args.iteraciones)
        graficar_boxplot_ejecuciones_instancia(args.instancia, args.ejecuciones, args.iteraciones)


if __name__ == "__main__":
    main()
