"""Punto de entrada del benchmark; la lógica está en src/benchmark.py."""

import sys
import argparse
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.benchmark import ejecutar_benchmark


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark AG, AM y ACS: Taillard 20x5, 50x10 y 100x10.")
    parser.add_argument('--iteraciones', type=int, default=100)
    parser.add_argument('--poblacion', type=int, default=30)
    parser.add_argument('--hormigas', type=int, default=30)
    parser.add_argument('--semilla', type=int, default=42)
    parser.add_argument('--instancias', nargs='+', help='Opcional: nombres concretos de data/.')
    parser.add_argument('--salida', help='Ruta CSV alternativa.')
    args = parser.parse_args()
    print(f"Resultados guardados en: {ejecutar_benchmark(**vars(args))}")
