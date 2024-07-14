"""
Funciones de la solución del problema de la facilidad de localización de
centros de distribución capacitados para satisfacer la demanda de alimentos
en los municipios.
"""
import os
import time
import warnings

import numpy as np
import pandas as pd
import pulp as pl
from scipy import cluster


def actualizar_resutados_ingenuos(resultados, key, ingenua):
    resultados["tipo_de_datos"].append(key)
    resultados["tipo_de_solucion"].append("ingenua")
    resultados["algoritmo_de_clusterizacion"].append("ninguno")
    resultados["costo_total"].append(ingenua[0])
    resultados["cantidad_de_centros_de_distribucion"].append(ingenua[1])
    resultados["tiempo_de_ejecucion"].append(ingenua[2])
    resultados["suma_de_demanda_por_cluster"].append(ingenua[3])
    resultados["suma_de_demanda_satisfecha_por_cluster"].append(ingenua[4])
    resultados["suma_de_capacidad_por_cluster"].append(ingenua[5])
    resultados["suma_de_capacidad_utilizada_por_cluster"].append(ingenua[6])
    resultados["estado"].append(
        "satisfecho" if ingenua[3] <= ingenua[5] else "insatisfecho"
    )
    return resultados


def leer_datos_solucion_cflp(comida_per_capita):
    datos_crudos = {
        "datos_completos": {
            "poblacion": pd.read_csv(
                "resultados/tablas/pronostico_poblacional/datos_completos.csv",
                index_col=0,
            )["Poblacion_2034"],
            "demanda": pd.read_csv(
                "resultados/tablas/pronostico_poblacional/datos_completos.csv",
                index_col=0,
            )["Poblacion_2034"].rename("demanda")
            * comida_per_capita
            * 7,  # 7 días de comida
            "lat": pd.read_csv("data/datos_completos/municipios.csv", index_col=0)[
                "lat"
            ],
            "lon": pd.read_csv("data/datos_completos/municipios.csv", index_col=0)[
                "lon"
            ],
            "capacidad": pd.read_csv(
                "resultados/tablas/capacidad_y_costo/demanda_completa.csv", index_col=0
            )["capacidad"],
            "precio": pd.read_csv(
                "resultados/tablas/capacidad_y_costo/demanda_completa.csv", index_col=0
            )["precio"],
            "kmeans": pd.read_csv(
                "resultados/tablas/clusteres/datos_completos.csv", index_col=0
            )["kmeans"],
            "som": pd.read_csv(
                "resultados/tablas/clusteres/datos_completos.csv", index_col=0
            )["som"],
            "agglomerative": pd.read_csv(
                "resultados/tablas/clusteres/datos_completos.csv", index_col=0
            )["agglomerative"],
            "dbscan": pd.read_csv(
                "resultados/tablas/clusteres/datos_completos.csv", index_col=0
            )["dbscan"],
        },
        "datos_imperfectos": {
            "poblacion": pd.read_csv(
                "resultados/tablas/pronostico_poblacional/datos_imperfectos.csv",
                index_col=0,
            )["Poblacion_2034"],
            "demanda": pd.read_csv(
                "resultados/tablas/pronostico_poblacional/datos_imperfectos.csv",
                index_col=0,
            )["Poblacion_2034"].rename("demanda")
            * comida_per_capita
            * 7,  # 7 días de comida
            "lat": pd.read_csv("data/datos_imperfectos/municipios.csv", index_col=0)[
                "lat"
            ],
            "lon": pd.read_csv("data/datos_imperfectos/municipios.csv", index_col=0)[
                "lon"
            ],
            "capacidad": pd.read_csv(
                "resultados/tablas/capacidad_y_costo/demanda_imperfecta.csv",
                index_col=0,
            )["capacidad"],
            "precio": pd.read_csv(
                "resultados/tablas/capacidad_y_costo/demanda_imperfecta.csv",
                index_col=0,
            )["precio"],
            "kmeans": pd.read_csv(
                "resultados/tablas/clusteres/datos_imperfectos.csv", index_col=0
            )["kmeans"],
            "som": pd.read_csv(
                "resultados/tablas/clusteres/datos_imperfectos.csv", index_col=0
            )["som"],
            "agglomerative": pd.read_csv(
                "resultados/tablas/clusteres/datos_imperfectos.csv", index_col=0
            )["agglomerative"],
            "dbscan": pd.read_csv(
                "resultados/tablas/clusteres/datos_imperfectos.csv", index_col=0
            )["dbscan"],
        },
    }
    matriz_de_costos = {
        "datos_completos": pd.read_csv(
            "data/datos_completos/matriz-de-costos.csv", index_col=0
        ),
        "datos_imperfectos": pd.read_csv(
            "data/datos_imperfectos/matriz-de-costos.csv", index_col=0
        ),
    }
    # unir los datos de los municipios en dataframes
    datos = {}
    for tipo_de_datos, datos_por_tipo in datos_crudos.items():
        datos[tipo_de_datos] = pd.concat(
            [
                datos_por_tipo["poblacion"],
                datos_por_tipo["demanda"],
                datos_por_tipo["lat"],
                datos_por_tipo["lon"],
                datos_por_tipo["capacidad"],
                datos_por_tipo["precio"],
                datos_por_tipo["kmeans"],
                datos_por_tipo["som"],
                datos_por_tipo["agglomerative"],
                datos_por_tipo["dbscan"],
            ],
            axis=1,
        )
        datos[tipo_de_datos].index.name = "divipola"
        datos[tipo_de_datos].index = datos[tipo_de_datos].index.astype(int)
        matriz_de_costos[tipo_de_datos].columns = matriz_de_costos[
            tipo_de_datos
        ].columns.astype(int)
        matriz_de_costos[tipo_de_datos].index = matriz_de_costos[
            tipo_de_datos
        ].index.astype(int)
    return datos, matriz_de_costos


def solucion_ingenua(
    datos, key
) -> tuple[float, int, float, float, float, float, float]:
    """
    Función para que utiliza la solución ingenua para resolver el problema de
    la facilidad de localización de centros de distribución capacitados para
    satisfacer la demanda de alimentos en los municipios.

    La función ingenua es aquella que asigna un centro de distribución por
    municipio.

    adicionalmente se crea un archivo de excel con los resultados de cada variable:
    i: Lista de potenciales centros de distribución
    j: Lista de municipios a los que se les asigna un centro de distribución
    Y_i: si un centro de distribución fue asignado o no {1, 0}
    X_ij: La cantidad en toneladas que satisface cada centro de distribución por municipio
    """
    tiempo_inicial = time.time()
    # el costo total es activar todos los lugares
    costo = sum(datos["precio"])
    cantidad_cd = len(datos)
    suma_de_demanda = sum(datos["demanda"])
    suma_de_demanda_por_cluster = suma_de_demanda
    suma_de_capacidad = sum(datos["capacidad"])
    suma_de_capacidad_utilizada = suma_de_demanda
    tiempo_final = time.time() - tiempo_inicial
    if suma_de_demanda > suma_de_capacidad:
        print("        No se puede satisfacer la demanda con la capacidad instalada")

    # crear el archivo de excel si no existe
    if not os.path.exists(
        f"resultados/tablas/solucionar_cflp/soluciones/{key}-ingenua.xlsx"
    ):
        print("        Creando archivo de excel", end="\r")
        # y vector de 1s
        y = [1] * len(datos)
        # x matriz de cantidad_cd x cantidad_cd con la diagonal igual a la demanda
        x = np.zeros((len(datos), len(datos)))
        np.fill_diagonal(x, datos["demanda"])
        # crear el dataframe
        df_x = pd.DataFrame(x, index=datos.index, columns=datos.index)
        df_y = pd.DataFrame(y, index=datos.index, columns=["Y"])
        # añadir una columna de 1s a y con el nombre de 'cluster'
        df_y["cluster"] = 1
        # añadir una columna con el nombre del 'municipio' a y
        df_y["municipio"] = pd.read_csv(f"data/{key}/municipios.csv", index_col=0).loc[
            datos.index, "municipio"
        ]
        with pd.ExcelWriter(
            f"resultados/tablas/solucionar_cflp/soluciones/{key}-ingenua.xlsx"
        ) as writer:
            df_x.to_excel(writer, sheet_name="X")
            df_y.to_excel(writer, sheet_name="Y")
        print("        Archivo de excel creado satisfactoriamente")
    return (
        costo,
        cantidad_cd,
        tiempo_final,
        suma_de_demanda,
        suma_de_demanda_por_cluster,
        suma_de_capacidad,
        suma_de_capacidad_utilizada,
    )


def actualizar_resultados_sin_clusterizar(
    resultados, key, value, cluster_id, sin_clusterizar
):
    resultados["tipo_de_datos"].append(key)
    resultados["tipo_de_solucion"].append("sin clusterizar")
    resultados["algoritmo_de_clusterizacion"].append("ninguno")
    resultados["costo_total"].append(sin_clusterizar[0])
    resultados["cantidad_de_centros_de_distribucion"].append(sin_clusterizar[1])
    resultados["tiempo_de_ejecucion"].append(sin_clusterizar[2])
    resultados["suma_de_demanda_por_cluster"].append(sin_clusterizar[4])
    resultados["suma_de_demanda_satisfecha_por_cluster"].append(sin_clusterizar[4])
    resultados["suma_de_capacidad_por_cluster"].append(sin_clusterizar[5])
    resultados["suma_de_capacidad_utilizada_por_cluster"].append(sin_clusterizar[6])
    resultados["estado"].append(sin_clusterizar[7])
    x = sin_clusterizar[8]
    y = sin_clusterizar[9]
    y["cluster"] = cluster_id
    y["municipio"] = pd.read_csv(f"data/{key}/municipios.csv", index_col=0).loc[
        value.index, "municipio"
    ]
    with pd.ExcelWriter(
        f"resultados/tablas/solucionar_cflp/soluciones/{key}-sin-clusterizar.xlsx"
    ) as writer:
        x.to_excel(writer, sheet_name="X")
        y.to_excel(writer, sheet_name="Y")
    return resultados

def actualizar_resultados_sin_clusterizar_a(
    resultados, key, value, cluster_id, sin_clusterizar
):
    resultados["tipo_de_datos"].append(key)
    resultados["tipo_de_solucion"].append("sin clusterizar")
    resultados["algoritmo_de_clusterizacion"].append("ninguno")
    resultados["costo_total"].append(sin_clusterizar[0])
    resultados["cantidad_de_centros_de_distribucion"].append(sin_clusterizar[1])
    resultados["tiempo_de_ejecucion"].append(sin_clusterizar[2])
    resultados["suma_de_demanda_por_cluster"].append(sin_clusterizar[4])
    resultados["suma_de_demanda_satisfecha_por_cluster"].append(sin_clusterizar[4])
    resultados["suma_de_capacidad_por_cluster"].append(sin_clusterizar[5])
    resultados["suma_de_capacidad_utilizada_por_cluster"].append(sin_clusterizar[6])
    resultados["estado"].append(sin_clusterizar[7])
    # x = sin_clusterizar[8]
    # y = sin_clusterizar[9]
    # y["cluster"] = cluster_id
    # y["municipio"] = pd.read_csv(f"data/{key}/municipios.csv", index_col=0).loc[
    #     value.index, "municipio"
    # ]
    # with pd.ExcelWriter(
    #     f"resultados/tablas/solucionar_cflp/soluciones/{key}-sin-clusterizar.xlsx"
    # ) as writer:
    #     x.to_excel(writer, sheet_name="X")
    #     y.to_excel(writer, sheet_name="Y")
    return resultados

def crear_diccionario_de_resultados():
    resultados = {
        "tipo_de_datos": [],
        "tipo_de_solucion": [],
        "algoritmo_de_clusterizacion": [],
        "costo_total": [],
        "cantidad_de_centros_de_distribucion": [],
        "tiempo_de_ejecucion": [],
        "estado": [],
        "suma_de_demanda_por_cluster": [],
        "suma_de_demanda_satisfecha_por_cluster": [],
        "suma_de_capacidad_por_cluster": [],
        "suma_de_capacidad_utilizada_por_cluster": [],
    }

    return resultados


def solucion_cflp_MC(datos, costos, tiempo_limite=60, log_path="logs/cflp.log"):
    """
    Función que resuelve cflp, crea el archivo de excel con los resultados y
    retorna los resultados de la solución sin clusterizar.

    formulación:
    SETS:
        i: Lista de potenciales centros de distribución
        j: Lista de municipios a que demandan alimentos
    VARIABLES:
        Y_i: si un centro de distribución fue asignado o no {1, 0}
        X_ij: La cantidad en toneladas que se transportan de i a j
    PARAMETROS:
        c[i, j]: costo de transportar una tonelada de alimentos de i a j
        f[i]: costo de activar un centro de distribución
        a[i]: capacidad de almacenamiento de i
        b[j]: demanda de alimentos de j
    OBJETIVO:
        Minimizar el costo total
            min F = sum_{i in I} sum_{j in J} c[i, j] * X_ij + sum_{i in I} f[i] * Y_i
    RESTRICCIONES:
        1. sum_{i in I} X_ij >= b[j] for all j in J
        2. sum_{j in J} X_ij <= a[i] * Y_i for all i in I
        3. X_ij >= 0 for all i in I, j in J
        4. Y_i = {0, 1} for all i in I

    retorna:
        costo_total: costo total de la solución
        cantidad_de_centros_de_distribucion: cantidad de centros de distribución
        tiempo_de_ejecucion: tiempo de ejecución de la solución
        suma_de_demanda: suma de la demanda
        suma_de_demanda_por_cluster: suma de la demanda por cluster
        suma_de_capacidad: suma de la capacidad
        suma_de_capacidad_utilizada: suma de la capacidad utilizada
        X: matriz de cantidad_cd x cantidad_cd con la cantidad de alimentos que se transporta de i a j
        Y: vector de 1s y 0s que indica si un centro de distribución fue asignado o no
    """
    warnings.filterwarnings("ignore", category=UserWarning)
    tiempo_inicial = time.time()

    # Sets
    I = range(len(datos))
    J = range(len(datos))
    # Variables
    Y = pl.LpVariable.dicts("Y", I, 0, 1, cat="Binary")
    X = pl.LpVariable.dicts("X", (I, J), 0, None, cat="Continuous")
    # Parámetros
    c = costos.values
    f = datos["precio"].values
    a = datos["capacidad"].values
    b = datos["demanda"].values
    # Crear el problema
    problema = pl.LpProblem("cflp", pl.LpMinimize)
    # Función objetivo
    problema += pl.lpSum(c[i, j] * X[i][j] for i in I for j in J) + pl.lpSum(
        f[i] * Y[i] for i in I
    )
    # Restricciones
    # restricción 1: Cumplir con la demanda
    for j in J:
        problema += pl.lpSum(X[i][j] for i in I) >= b[j], f"demanda_{j}"
    # restricción 2: Capacidad de almacenamiento si se abre
    for i in I:
        problema += pl.lpSum(X[i][j] for j in J) <= a[i] * Y[i], f"capacidad_{i}"
    # resolver el problema
    solver = pl.PULP_CBC_CMD(timeLimit=tiempo_limite, logPath=log_path)
    problema.solve(solver)
    tiempo_de_ejecucion = time.time() - tiempo_inicial
    # resultados
    costo_total = pl.value(problema.objective)
    df_y = pd.DataFrame([pl.value(Y[i]) for i in I], index=datos.index, columns=["Y"])
    df_x = pd.DataFrame(
        [[pl.value(X[i][j]) for j in J] for i in I],
        index=datos.index,
        columns=datos.index,
    )

    # estado, teniendo en cuenta si se pasa del tiempo
    print("-" * 100, end="\r")
    if pl.LpStatus[problema.status] == "Optimal":
        # Revisar si se detuvo por tiempo o por óptimo
        if solver.timeLimit is not None and solver.timeLimit <= tiempo_de_ejecucion:
            print("        Se detuvo por tiempo")
            estatus = "Detenido por tiempo"
        else:
            print("        Óptimo encontrado")
            estatus = "Óptimo"
    else:
        print("        No se encontró solución")
        estatus = pl.LpStatus[problema.status]
    cantidad_de_centros_de_distribucion = df_y["Y"].sum()
    suma_de_demanda = sum(datos["demanda"])
    suma_de_demanda_por_cluster = sum(df_x.sum())
    suma_de_capacidad = sum(datos["capacidad"])
    suma_de_capacidad_utilizada = sum(df_x.sum())

    return (
        costo_total,
        cantidad_de_centros_de_distribucion,
        tiempo_de_ejecucion,
        suma_de_demanda,
        suma_de_demanda_por_cluster,
        suma_de_capacidad,
        suma_de_capacidad_utilizada,
        estatus,
        df_x,
        df_y,
    )


def solucionar_cflp(comida_per_capita, tiempo_maximo=60 * 60):
    """
    Función para solucionar el problema de la facilidad de localización de
    centros de distribución capacitados para satisfacer la demanda de
    alimentos en los municipios.

    Pseudocódigo:
    para cada tipo de datos [datos_completos, datos_imperfectos]

    1. Leer los datos necesarios.
        - Datos de los municipios.
            - divipola (primera columna de todos los archivos)
            - población (resultados/tablas/pronostico_poblacional/{datos_completos, datos_imperfectos}.csv) - columna ['Poblacion_2034']
            - lat y lon (data/{datos_completos, datos_imperfectos}/municipios.csv) - columnas ['lat', 'lon'] o (resultados/tablas/clusteres/{datos_completos, datos_imperfectos}.csv) - columnas ['lat', 'lon']
            - capacidad de almacenamiento  (resultados/tablas/capacidad_y_costo/{demanda_completa, demanda_imperfecta}.csv) - columna ['capacidad']
            - costo de almacenamiento (resultados/tablas/capacidad_y_costo/{demanda_completa, demanda_imperfecta}.csv) - columna ['precio']
            - cluster al que pertenece (resultados/tablas/clusteres/{datos_completos, datos_imperfectos}.csv) - columnas ['kmeans', 'som', 'agglomerative', 'dbscan']
        - Datos de costos de transporte. (data/{datos_completos, datos_imperfectos}/matriz-de-costos.csv)
            - divipola origen (primera columna de todos los archivos)
            - divipola destino (primera fila de todos los archivos [encabezado])
            - costo de transporte (resto de la matriz)
        # revisar que columnas e indices queden como enteros
    [Poblacion_2034	demanda	lat	lon	capacidad	precio	kmeans	som	agglomerative	dbscan]
    2. Ordenar y estructurar los datos [crear la demanda=poblacion*comida_per_capita*7].
    3. Crear diccionario que recolectará los resultados.
        - tipo de datos [datos_completos, datos_imperfectos]
        - tipo de solución [ingenua, sin clusterizar, clusterizada]
        - algoritmo de clusterización [k-means, som, agglomerative, dbscan]
        - costo total
        - cantidad de centros de distribución
        - tiempo de ejecución
        - suma de la demanda por cluster
        - suma de demanda satisfecha por cluster
        - suma de la capacidad por cluster
        - suma de la capacidad utilizada por cluster
    4. Resolver el problema para cada tipo de solución.
        - Solución ingenua.
        - Solución sin clusterizar.
        - Solución clusterizada.
    5. Guardar los resultados en un archivo csv.
    """
    datos, matriz_de_costos = leer_datos_solucion_cflp(comida_per_capita)
    resultados = crear_diccionario_de_resultados()
    for key, value in datos.items():
        costos = matriz_de_costos[key]
        print(f"Resolviendo el problema para {key}")

        ####* Solución ingenua ####
        print("    Procesando solución ingenua", end="\r")
        ingenua = solucion_ingenua(value, key)
        resultados = actualizar_resutados_ingenuos(resultados, key, ingenua)
        print("    Solución ingenua procesada satisfactoriamente")

        ####* Solución sin clusterizar ####
        # cluster_id = 1
        # print("    Procesando solución sin clusterizar", end="\r")
        # sin_clusterizar = solucion_cflp_MC(
        #     value,
        #     costos,
        #     tiempo_limite=tiempo_maximo,
        #     log_path=f"resultados/logs/cflp-{key}-sin-clusterizar.log",
        # )
        # resultados = actualizar_resultados_sin_clusterizar(
        #     resultados, key, value, cluster_id, sin_clusterizar
        # )
        # print("    Solución sin clusterizar procesada satisfactoriamente")

        ####* Solución clusterizada ####
        print("    Procesando solución clusterizada", end="\r")
        lista_modelos = ["kmeans", "som", "agglomerative", "dbscan"]
        for modelo in lista_modelos:
            print(f"        Procesando modelo {modelo}")
            resultados_de_cluster, df_y, df_x = solucion_clusterizada(
                tiempo_maximo, key, value, costos, modelo
            )
            resultados = actualizar_resultados_clusterizados(
                resultados, key, modelo, resultados_de_cluster, df_y, df_x
            )
        print("    Solución clusterizada procesada satisfactoriamente")

    # Guardar los resultados en un archivo csv
    resultados = pd.DataFrame(resultados)
    resultados.to_csv(
        "resultados/tablas/solucionar_cflp/metricas/cflp.csv", index=False
    )


def solucion_clusterizada(tiempo_maximo, key, value, costos, modelo):
    resultados_de_cluster = crear_diccionario_de_resultados()
    df_y = pd.DataFrame(columns=["Y", "cluster", "municipio"], index=value.index)
    df_x = pd.DataFrame(columns=value.index, index=value.index)
    lista_de_clusteres = value[modelo].unique()
    for cluster_id in lista_de_clusteres:
        print(f"            Procesando cluster {cluster_id}", end="\r")
        cluster_value = value[value[modelo] == cluster_id]
        cluster_costos = costos.loc[cluster_value.index, cluster_value.index]
        cluster_solucion = solucion_cflp_MC(
            cluster_value,
            cluster_costos,
            tiempo_limite=tiempo_maximo,
            log_path=f"resultados/logs/cflp-{key}-{modelo}-{cluster_id}.log",
        )
        resultados_de_cluster = actualizar_resultados_sin_clusterizar_a(
            resultados_de_cluster,
            key,
            cluster_value,
            cluster_id,
            cluster_solucion,
        )
        df_y_to_add = cluster_solucion[9]
        df_y_to_add["cluster"] = cluster_id
        df_y_to_add["municipio"] = pd.read_csv(
            f"data/{key}/municipios.csv", index_col=0
        ).loc[cluster_value.index, "municipio"]

        df_y = df_y.combine_first(cluster_solucion[9])
        df_x = df_x.combine_first(cluster_solucion[8])
    return resultados_de_cluster, df_y, df_x


def actualizar_resultados_clusterizados(
    resultados, key, modelo, resultados_de_cluster, df_y, df_x
):
    # Calcular las métricas de los clusteres
    # costo total = suma
    costo_total = sum(resultados_de_cluster["costo_total"])
    # cantidad de centros de distribución = suma
    cantidad_de_centros_de_distribucion = sum(
        resultados_de_cluster["cantidad_de_centros_de_distribucion"]
    )
    # tiempo de ejecución = suma
    tiempo_de_ejecucion = sum(resultados_de_cluster["tiempo_de_ejecucion"])
    # suma de la demanda = suma
    suma_de_demanda = sum(resultados_de_cluster["suma_de_demanda_por_cluster"])
    # suma de la demanda por cluster = datos originales
    suma_de_demanda_por_cluster = resultados_de_cluster["suma_de_demanda_por_cluster"]
    # suma de la capacidad = suma
    suma_de_capacidad = sum(resultados_de_cluster["suma_de_capacidad_por_cluster"])
    # suma de la capacidad utilizada = datos originales
    suma_de_capacidad_utilizada = resultados_de_cluster[
        "suma_de_capacidad_utilizada_por_cluster"
    ]
    # estado = datos originales
    estado = resultados_de_cluster["estado"]

    # Añadir los resultados al diccionario de resultados
    resultados["tipo_de_datos"].append(key)
    resultados["tipo_de_solucion"].append("clusterizada")
    resultados["algoritmo_de_clusterizacion"].append(modelo)
    resultados["costo_total"].append(costo_total)
    resultados["cantidad_de_centros_de_distribucion"].append(
        cantidad_de_centros_de_distribucion
    )
    resultados["tiempo_de_ejecucion"].append(tiempo_de_ejecucion)
    resultados["suma_de_demanda_por_cluster"].append(suma_de_demanda)
    resultados["suma_de_demanda_satisfecha_por_cluster"].append(
        suma_de_demanda_por_cluster
    )
    resultados["suma_de_capacidad_por_cluster"].append(suma_de_capacidad)
    resultados["suma_de_capacidad_utilizada_por_cluster"].append(
        suma_de_capacidad_utilizada
    )
    resultados["estado"].append(estado)
    # Crear el archivo de excel
    with pd.ExcelWriter(
        f"resultados/tablas/solucionar_cflp/soluciones/{key}-{modelo}.xlsx"
    ) as writer:
        df_x.to_excel(writer, sheet_name="X")
        df_y.to_excel(writer, sheet_name="Y")
    return resultados
