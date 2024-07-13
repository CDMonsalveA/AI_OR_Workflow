"""
K Propuesta

Este script contiene la función que propone un valor de k clústeres para
la división de municipios para el problema de cflp.
"""
import os
import time
import warnings

import numpy as np
import pandas as pd
import pulp as pl
from sklearn.preprocessing import MinMaxScaler



def k_propuesta(
    D_ij: pd.DataFrame,
    M: int | None,
    muestra_size: float = 0.1,
    lambda_: float | None = None,
    random_seed: int = 11,
    id_data: str = "0",
    tiempo_max: int = 60,
) -> tuple[int, float, str]:
    """
    Función que propone un valor de k clústeres para
    la división de municipios para el problema de
    cflp.

    Parameters
    ----------
    D_ij : pd.DataFrame
        Matriz de distancias entre municipios.
    M : int
        Número máximo de municipios por centro de
        distribución.
          (predeterminado es el tamaño de la muestra).
    lambda_ : float
        Factor de penalización de generación de centroides.
          (predeterminado es 1 + len(D_ij) / M * muestra_size ).
    random_seed : int
        Semilla para reproducibilidad.

    Returns
    -------
    k_propuesto : int
        Número de clústeres propuesto.

    Pseudocódigo
    ------------
    1. Seleccionar una muestra de la matriz D_ij.
    2. Normalizar los datos usando el MinMaxScaler.
    3. Solucionar el problema de optimización
    4. Retornar el valor de k = sum(y_j)

    Optimización
    ------------
    Sets:
        i = 1, 2, ..., n (Lista de ubicaciones)
        j = 1, 2, ..., m (Lista de posibles centroides)
    Parámetros:
        D_ij = Distancia entre i y j
        M = Número máximo de ubicaciones por centro
        lambda_ = Factor de penalización
    Variables:
        x_ij = 1 si la ubicación i es asignada al centro j
        y_j = 1 si el centro j es abierto
    Función objetivo:
        min sum(D_ij * x_ij) + lambda_ * sum(y_j)
    Restricciones:
        sum(x_ij) = 1 para todo i
        sum(x_ij) <= M * y_j para todo j
        x_ij pertenecen a {0, 1}
        y_j pertenecen a {0, 1}
    """
    warnings.filterwarnings("ignore", category=UserWarning)
    # 1. Seleccionar una muestra de la matriz D_ij.
    D_ij = D_ij.sample(frac=muestra_size, random_state=random_seed, axis=0)
    D_ij = D_ij.sample(frac=muestra_size, random_state=random_seed, axis=1)  # type: ignore
    # 2. Normalizar los datos usando el MinMaxScaler.
    scaler = MinMaxScaler()
    D_ij = pd.DataFrame(
        scaler.fit_transform(D_ij), index=D_ij.index, columns=D_ij.columns
    )
    # 3. Solucionar el problema de optimización
    n, m = D_ij.shape
    if M is None:
        M = n
    if lambda_ is None:
        lambda_ = 1 + n / M * muestra_size
    # Crear el problema de optimización
    I = range(n)
    J = range(m)
    prob = pl.LpProblem("Buscar_K", pl.LpMinimize)
    # Variables
    x = pl.LpVariable.dicts("x", (I, J), 0, 1, pl.LpBinary)
    y = pl.LpVariable.dicts("y", J, 0, 1, pl.LpBinary)
    # Función objetivo
    prob += pl.lpSum(
        D_ij.iloc[i, j] * x[i][j] for i in I for j in J
    ) + lambda_ * pl.lpSum(y[j] for j in J)
    # Restricciones
    for i in I:
        prob += pl.lpSum(x[i][j] for j in J) == 1
    for j in J:
        prob += pl.lpSum(x[i][j] for i in I) <= M * y[j]
    # Resolver el problema
    prob.solve(
        solver=pl.PULP_CBC_CMD(
            logPath=f"resultados/logs/4. cantidad_de_clusteres/{id_data}{muestra_size:.2f}.log",
            threads=os.cpu_count(),
            timeLimit=tiempo_max,
        )
    )
    # 4. Retornar el valor de k = sum(y_j)
    k = sum([y[j].varValue for j in J])

    if n == 0:
        return k, 0, "No hay municipios"
    else:
        return k, (prob.objective.value() / n), pl.LpStatus[prob.status] # type: ignore

def cantidad_de_clusteres(RANDOM_SEED, tiempo_maximo=60, rango_de_muestras= np.linspace(0.05, 0.3, 30)):
    archivos_a_crearse = [
    "resultados/tablas/cantidad_de_clusteres/datos_completos.csv",
    "resultados/tablas/cantidad_de_clusteres/datos_imperfectos.csv",
]
    if all([os.path.exists(archivo) for archivo in archivos_a_crearse]):
        print("\nLa propuesta de k para los datos ya fue generada.")
        return

    datos = {
    "datos_completos": pd.read_csv(
        "data/datos_completos/matriz-de-distancias.csv", index_col=0
    ),
    "datos_imperfectos": pd.read_csv(
        "data/datos_imperfectos/matriz-de-distancias.csv", index_col=0
    ),
}

    for key, value in datos.items():
        k_propuestos = {
        "k": [],
        "error": [],
        "tiempo": [],
        "muestra": [],
        "estatus": [],
    }
        print(f"Proponiendo k para {key}")
        progreso = 0
        muestras = rango_de_muestras
        for muestra in muestras:
            tiempo_inicial = time.time()
            propuesta = k_propuesta(
            D_ij=value,
            M=None,
            muestra_size=muestra,
            lambda_=None,
            random_seed=RANDOM_SEED,
            id_data=key,
            tiempo_max=tiempo_maximo,
        )
            tiempo_final = time.time()

            k_propuestos["k"].append(propuesta[0])
            k_propuestos["error"].append(propuesta[1])

            k_propuestos["tiempo"].append(tiempo_final - tiempo_inicial)
            k_propuestos["muestra"].append(muestra)
            if k_propuestos["tiempo"][-1] > 60:
                k_propuestos["estatus"].append("Tiempo de ejecución excedido")
            else:
                k_propuestos["estatus"].append(propuesta[2])
            progreso += 1
            print(f"  Progreso: {(progreso)/len(muestras)*100:.2f}%", end="\r")

    # Guardar los resultados
        pd.DataFrame(k_propuestos).to_csv(
        f"resultados/tablas/cantidad_de_clusteres/{key}.csv", index=False
    )
        print(f"  Terminado para {key}")
