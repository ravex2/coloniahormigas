import numpy as np
import os


# individuos, y poblacion en la asociacion del algiritmo genetico
def fitness_pfsp(permutacion, tiempos):
    cantidad_maquinas = tiempos.shape[0]
    finalizacion_maquinas = np.zeros(cantidad_maquinas, dtype=np.int64)

    for trabajo in permutacion:
        finalizacion_trabajo = np.int64(0)
        for maquina in range(cantidad_maquinas):
            inicio = max(finalizacion_trabajo, finalizacion_maquinas[maquina])
            finalizacion_trabajo = inicio + tiempos[maquina, trabajo]
            finalizacion_maquinas[maquina] = finalizacion_trabajo

    return int(finalizacion_maquinas[-1])

