"""
Funciones para la generación de clusteres de municipios
"""
import os
import time
from math import ceil, floor, sqrt

import numpy as np
import pandas as pd

from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.metrics import (
    silhouette_score,
    calinski_harabasz_score,
    davies_bouldin_score,
)
from sklearn_som.som import SOM


# Generar los grupos de clusteres
def generar_clusteres(random_seed, n_cluster_completo=6, n_cluster_imperfecto=6):
    """
    Función que toma los datos de municipios, latitud y longitud,
    y los clusteriza en grupos de municipios que se encuentran
    cerca geográficamente.

    los métodos de clusterización son:
        1. k-means
        2. Mapa Autoorganizado
        3. Agrupamiento Jerárquico
        4. DBSCAN

    Reporta las métricas de calidad de los clusteres generados.
    Guarda los resultados en la carpeta /resultados/tablas/clusteres/

    para los datos_completos y los datos_imperfectos.


    Parámetros
    ----------
    random_seed : int
        Semilla para la generación de números aleatorios.
    """
    archivos_a_generar = [
        "resultados/tablas/clusteres/metricas-datos_completos.csv",
        "resultados/tablas/clusteres/metricas-datos_imperfectos.csv",
        "resultados/tablas/clusteres/datos_completos.csv",
        "resultados/tablas/clusteres/datos_imperfectos.csv",
    ]
    if all([os.path.exists(archivo) for archivo in archivos_a_generar]):
        print("\nLas tablas de clusteres ya han sido generadas.")
        return

    # 1. Leer los datos
    datos = {
        "datos_completos": pd.read_csv(
            "data/datos_completos/municipios.csv", index_col=0
        )[["lat", "lon"]],
        "datos_imperfectos": pd.read_csv(
            "data/datos_imperfectos/municipios.csv", index_col=0
        )[["lat", "lon"]],
    }
    n_cluster = {
        "datos_completos": n_cluster_completo,
        "datos_imperfectos": n_cluster_imperfecto,
    }
    for key, value in datos.items():
        print(f"Generando clusteres para {key}")
        # 2. Definir los modelos
        modelos = modelos_de_clusteres(n_cluster[key], random_seed)
        # 3. Generar las columnas de clusteres |divipola|kmeans|som|agglomerative|dbscan|
        progreso = 0
        metricas = {
            "Modelo": [],
            "cantidad_de_clusteres": [],
            "tamanos_de_clusteres": [],
            "silhouette_score": [],
            "calinski_harabasz_score": [],
            "davies_bouldin_score": [],
            "tiempo": [],
        }
        for key_modelo, modelo in modelos.items():
            progreso += 1
            print(f"    {key_modelo}, progreso: {progreso/len(modelos)*100:.2f}%")
            tiempo_inicial = time.time()
            value[f"{key_modelo}"] = clusterizar(
                value[["lat", "lon"]], key_modelo, modelo
            )
            tiempo_final = time.time()
            metricas["Modelo"].append(key_modelo)
            metricas["cantidad_de_clusteres"].append(
                len(np.unique(value[f"{key_modelo}"]))
            )
            metricas["tamanos_de_clusteres"].append(
                value[f"{key_modelo}"].value_counts().values
            )
            metricas["silhouette_score"].append(
                silhouette_score(value[["lat", "lon"]], value[f"{key_modelo}"])
            )
            metricas["calinski_harabasz_score"].append(
                calinski_harabasz_score(value[["lat", "lon"]], value[f"{key_modelo}"])
            )
            metricas["davies_bouldin_score"].append(
                davies_bouldin_score(value[["lat", "lon"]], value[f"{key_modelo}"])
            )
            metricas["tiempo"].append(tiempo_final - tiempo_inicial)

        # 4. Sacar métricas y estadísticas por modelo
        # ordenar tamaño de clusteres para que quede en forma de columnas que van desde el minimo hasta el máximo
        metricas = pd.DataFrame(metricas)
        # 5. Guardar las métricas y estadísticas en /resultados/tablas/clusteres/
        metricas.to_csv(f"resultados/tablas/clusteres/metricas-{key}.csv")
        # 6. Guardar los datos de clusteres en /resultados/datos/clusteres/
        value.to_csv(f"resultados/tablas/clusteres/{key}.csv")


def modelos_de_clusteres(n_cluster, random_seed):
    """
    Función que genera los modelos de clusteres para los datos
    de municipios.

    Los modelos son:
        1. k-means
        2. Mapa Autoorganizado
        3. Agrupamiento Jerárquico
        4. DBSCAN

    Parámetros
    ----------
    n_cluster : int
        Número de clusteres a generar.
    random_seed : int
        Semilla para la generación de números aleatorios.

    Retorna
    -------
    modelos : dict
        Diccionario con los modelos de clusteres.
    """
    modelos = {
        "kmeans": KMeans(n_clusters=n_cluster, random_state=random_seed),
        "som": SOM(
            m=floor(sqrt(n_cluster)),
            n=ceil(sqrt(n_cluster)),
            dim=2,
            random_state=random_seed,
        ),
        "agglomerative": AgglomerativeClustering(n_clusters=n_cluster),
        "dbscan": DBSCAN(eps=0.5, min_samples=int(n_cluster / 2)),
    }
    return modelos


def clusterizar(
    datos: pd.DataFrame,
    key_modelo: str,
    modelo: KMeans | SOM | AgglomerativeClustering | DBSCAN,
):
    """
    Función que toma los datos de municipios, latitud y longitud,
    y los clusteriza en grupos de municipios que se encuentran
    cerca geográficamente.

    Parámetros
    ----------
    datos : pd.DataFrame
        Datos de municipios con las columnas latitud y longitud.
    key_modelo : str
        Nombre del modelo de clusterización.
    modelo : sklearn.cluster | sklearn_som.som
        Modelo de clusterización.

    Retorna
    -------
    clusteres : pd.Series
        Serie con los clusteres generados.
    """
    if key_modelo == "som":
        clusteres = modelo.fit_predict(datos.values)
    else:
        modelo.fit(datos.values)
        clusteres = modelo.labels_ # type: ignore
    return pd.Series(clusteres, index=datos.index)
