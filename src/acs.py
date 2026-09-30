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
def random_hormiga(seed,m_completa,num_hormigas):
    random.seed(seed)
    n_hormiga = num_hormigas
    


def dis(p1,p2):
    d1 = math.pow(p2[0] - p1[0],2)
    d2 = math.pow(p2[1] - p1[1],2)
    return math.sqrt(d1+d2)


'''
pero antes tenemos una matiz de corrdenadas (x,y) dentro de la matriz -> vamos a usar los infices
cada dij -> numero que es una distancia
'''
def crear_matriz_coordendadas(num_hormigas):


# matrz euristica np.fulllike