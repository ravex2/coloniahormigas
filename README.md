# Proyecto 2 - PFSP con AG, AM y ACS

Implementación modular del **Permutation Flow Shop Scheduling Problem (PFSP)** con tres
metaheurísticas: Algoritmo Genético (AG), Algoritmo Memético (AM) y Ant Colony System
(ACS). Cada solución es una permutación de trabajos y se evalúa minimizando el makespan
`C_max`.

## Requisitos e instalación

Se requiere Python 3.10+, NumPy y pandas. Para generar gráficos también se requiere Matplotlib.

```bash
python3 -m pip install -r requirements.txt
```

Las 120 instancias de Taillard se encuentran en `data/`. Los números de trabajo que se
escriben en los CSV son 1-indexados; internamente Python utiliza índices desde cero.

## Ejecución individual

Cada metaheurística tiene su propio punto de entrada y archivo de resultados CSV.

```bash
# Algoritmo Genético
python3 ag.py ta001.txt --poblacion 40 --iteraciones 200 --semilla 42

# Algoritmo Memético (AG + búsqueda local por inserción)
python3 am.py ta001.txt --poblacion 40 --iteraciones 200 --frecuencia-local 5

# Ant Colony System
python3 acs.py ta001.txt --hormigas 30 --iteraciones 200 --alpha 0.1 --beta 2 --q0 0.8

# ACS sobre los 52 nodos del TSP Berlin52
python3 acs.py berlin52.tsp --hormigas 30 --iteraciones 500 --alpha 0.1 --beta 2 --q0 0.8 --salida resultados/acs_berlin52.csv
```


## Comparación y gráfico

El benchmark predeterminado compara AG, AM y ACS en 30 instancias Taillard:

| Categoría | Trabajos × máquinas | Instancias |
|---|---|---|
| Pequeña | 20 × 5 | ta001–ta010 |
| Mediana | 50 × 10 | ta041–ta050 |
| Grande | 100 × 10 | ta071–ta080 |

```bash
cd /script
run_benchmark.py --iteraciones 100 --semilla 42

cd src

graficos.py --benchmark
# Curva independiente de ACS PFSP
graficos.py --acs --instancia ta071.txt --iteraciones 100
```


## Estructura

```text
ag.py, am.py, acs.py  puntos de entrada independientes
main.py               comparador de los tres algoritmos
src/pfsp.py           lector Taillard y cálculo de C_max
src/ag_build.py       implementación del AG y sus operadores de permutación
src/am_build.py       implementación del AM y búsqueda local
src/acs_build.py      ACS con actualización local y global de feromona
src/operadores.py     biblioteca común: Instancia, TipoProblema, PFSP, Taillard y C_max
src/salidas.py        resultados CSV reproducibles
src/graficos.py       gráficos de AG, AM y ACS
src/benchmark.py      benchmark de AG, AM y ACS
data/                 instancias Taillard
resultados/           salidas generadas (ignoradas por Git)
graficos/             gráficos generados (ignorados por Git)
```



Los componentes de la lista de cotejo están explícitos en `src/acs_build.py`:

Todas las ejecuciones aceptan `--semilla`, de modo que el experimento es reproducible.

Los lectores devuelven una estructura genérica `Instancia`: `datos` contiene la matriz o
coordenadas del dataset y `metadatos` conserva sus atributos particulares. Así se pueden
agregar nuevos lectores sin crear una clase distinta por cada formato.

