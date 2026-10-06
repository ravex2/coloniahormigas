import numpy as np
import random
import pandas as pd
import math

''' leer los archivos y pasarlos al fotmato'''
def berlin(entrada):
    mc = pd.read_table(entrada,header=None,sep=r'\s+',skiprows=6, skipfooter=2)
    mc = mc.drop(columns=0).to_numpy()
    print("coordenada shape: ", mc.shape)
    numvariables = mc.shape[0]
    print(mc)

def calcular_distance(numVariables):
    d = np.full((numVariables,numVariables),fill_value=-1.0,dtype=float)
    for i in range(numVariables-1):
        for j in range(i+1,numVariables):
            d[i][j] = np.sqrt(np.sum(np.square(d[i]-d[j])))
            d[i][j] = d[j][i]

            #value = (i,j)
            #d[i][j] = dis(value[0],value[1])

# esta debe se 1/d
def calcular_matriz_heuristica(d):
    h = np.full_like(1/d,fill_value=-1.0,dtype=float)
    print(h)

# se calcula ffilas n hormigas y c t52 -> (0,52)
def random_hormiga(seed,m_completa: int,num_hormigas: int):
    random.seed(seed)
    n_hormiga = np.random().randint(0,num_hormigas-1)
    p_camino = np.random().randint(0,m_completa-1)
    return (n_hormiga,p_camino)


# para una sola hormiga se calcula la funcion de costos -> matriz de costos
def crear_funcion_costo(dimensiones):
    p = random.randint(0,dimensiones-1)
    a = random.randint(0,dimensiones-1)
    p_hormiga = (p,a)
    func_costos = np.full((dimensiones,dimensiones),fill_value=-1.0,dtype=float)
    print(p_hormiga)
    print(func_costos)
    for i in range(dimensiones):
        for j in range(dimensiones):
            if (i, j) == p_hormiga:
                func_costos[i][j] = 1
    print(func_costos)
    return func_costos


def feromona_inicial(tiempo, alpha):
    pass


def crear_matriz_feromonas(dimension):
    tm = np.full((dimension,dimension),fill_value=-1.0,dtype=float)


    
def crear_matriz_colonia():
    pass



def acs_algo():
    pass



'''
def dis(p1,p2):
    d1 = math.pow(p2[0] - p1[0],2)
    d2 = math.pow(p2[1] - p1[1],2)
    return math.sqrt(d1+d2)
'''


'''
pero antes tenemos una matiz de corrdenadas (x,y) dentro de la matriz -> vamos a usar los infices
cada dij -> numero que es una distancia
'''


# matrz euristica np.fulllike