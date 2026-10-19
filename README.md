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

Para Berlin52, pandas lee las filas `id x y` de TSPLIB y se descarta la columna `id`;
NumPy crea después la matriz de distancias entre nodos.

Se puede indicar una ruta absoluta a la instancia y cambiar la salida, por ejemplo
`--salida resultados/experimento_ag.csv`.

## Comparación y gráfico

El benchmark predeterminado compara AG, AM y ACS en 30 instancias Taillard:

| Categoría | Trabajos × máquinas | Instancias |
|---|---|---|
| Pequeña | 20 × 5 | ta001–ta010 |
| Mediana | 50 × 10 | ta041–ta050 |
| Grande | 100 × 10 | ta071–ta080 |

```bash
venv/bin/python script/run_benchmark.py --iteraciones 100 --semilla 42
venv/bin/python src/graficos.py --benchmark
# Curva independiente de ACS PFSP
venv/bin/python src/graficos.py --acs --instancia ta071.txt --iteraciones 100
```

El CSV incluye makespan, RPD y tiempo de los tres algoritmos, categoría y parámetros
principales. `benchmark_por_tamano.png` separa las tres métricas por tamaño e incluye
ACS. Las cajas muestran variación entre instancias con una semilla; no representan
variabilidad entre semillas. Igual número de iteraciones no implica igual tiempo de cómputo.
Para seleccionar instancias usa `--instancias ta001.txt ta041.txt ta071.txt`.
`--salida` permite otro CSV; los gráficos lo reciben con `--benchmark --csv RUTA`.

`main.py` ejecuta AG, AM y ACS sobre la misma instancia y guarda una fila por algoritmo
en `resultados/comparacion.csv`. La opción `--grafico` crea el PNG de convergencia.

```bash
python3 main.py ta001.txt --iteraciones 200 --poblacion 40 --hormigas 30 --grafico
```

`src/graficos.py` genera gráficos comparativos que incluyen los tres algoritmos. Para una
instancia, dibuja convergencia y variabilidad entre semillas; para gráficos RPD/makespan
entre instancias, ejecute primero el benchmark.

```bash
python3 script/run_benchmark.py
python3 src/graficos.py --benchmark
# o bien, para una instancia concreta
python3 src/graficos.py --instancia ta001.txt --iteraciones 100 --ejecuciones 20
```

## Verificación

```bash
python3 -m unittest tests.py
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

## Parámetros principales

### Uso de NumPy y pandas

- **pandas** lee las tablas de tiempos Taillard y coordenadas TSPLIB, y escribe
  los resultados individuales y del benchmark mediante `DataFrame.to_csv()`.
- **NumPy** mantiene las matrices del motor, calcula distancias y evalúa de forma
  vectorizada los pesos de transición ACS y las aristas del tour completo.
- Las tablas se convierten a arrays al cargarlas, evitando crear DataFrames dentro
  de los bucles de optimización. La suma vectorizada puede producir diferencias
  mínimas de redondeo en costos TSP de punto flotante.

Los componentes de la lista de cotejo están explícitos en `src/acs_build.py`:

| Componente | Función |
|---|---|
| Colonia | `construir_colonia()` |
| Función de costos | `funcion_costos()` |
| Heurística | `calcular_heuristica()` |
| Feromona inicial | `inicializar_feromona()` |
| Regla de transición | `regla_transicion()` |
| Actualización local | `actualizar_feromona_local()` |
| Actualización global | `actualizar_feromona_global()` |

Los ejecutores PFSP y TSP llaman a estos componentes. `funcion_costos()` utiliza
el evaluador común `calcular_makespan()` para PFSP y `longitud_tour()` para TSP.
En los componentes, `datos` significa tiempos PFSP o distancias TSP; las coordenadas
se convierten previamente mediante `matriz_distancias()`.

- **AG/AM:** población, iteraciones, probabilidad de cruce OX y mutación por intercambio.
- **AM:** frecuencia y presupuesto de evaluaciones para búsqueda local por inserción de
  mejor mejora. La población incorpora una solución inicial NEH y la búsqueda nunca acepta
  un movimiento que empeore el `C_max`.
- **ACS:** número de hormigas, factor de evaporación `alpha`, peso heurístico `beta` y
  probabilidad de explotación `q0`. La transición y las actualizaciones local/global siguen
  directamente las ecuaciones del capítulo AMIN.

Todas las ejecuciones aceptan `--semilla`, de modo que el experimento es reproducible.

Los lectores devuelven una estructura genérica `Instancia`: `datos` contiene la matriz o
coordenadas del dataset y `metadatos` conserva sus atributos particulares. Así se pueden
agregar nuevos lectores sin crear una clase distinta por cada formato.

# Simulación conectada al código base

Desde esta carpeta ejecuta `venv/bin/python simulation/server.py` y abre
`http://127.0.0.1:8080`. ACS ejecuta Berlin52; AG y AM ejecutan `data/ta001.txt`.
**Solo debes ejecutar ese servidor:** no necesitas iniciar `main.py`, `ag.py`,
`am.py` ni `acs.py` por separado. La interfaz solicita al servidor la ejecución
del algoritmo seleccionado, y este llama directamente al código de `src/*_build.py`.
Una vez terminado el cálculo, el navegador reproduce sus estados reales.
Pausar y cambiar la velocidad afectan la reproducción; cambiar de algoritmo,
agentes o exploración solicita un nuevo cálculo. Reiniciar vuelve al primer estado
de la ejecución disponible. Mantén la terminal abierta y usa Ctrl+C para detenerla.

La interfaz reproduce estados reales capturados por observadores opcionales en
los algoritmos. Incluye tour y feromonas ACS, Gantt PFSP e historial de costo.
Consulta [simulation/README.md](simulation/README.md) para la preparación del entorno,
el funcionamiento y los límites de la visualización.
