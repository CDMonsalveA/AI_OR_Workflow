"""
Alistamiento de los datos para el modelo de optimización
"""

import os
import warnings
import geopy.distance
import numpy as np
import pandas as pd


def cargar_datos():
    """
    Cargar los datos de los archivos .csv y .xlsx

    Returns
    -------
    matriz_de_costos : pd.DataFrame
        Matriz de costos de transporte entre municipios sacados del SiceTac
    matriz_de_distancias : pd.DataFrame
        Matriz de distancias entre todos los municipios de Colombia por carretera con OpenStreetMap
    municipios : pd.DataFrame
        Información de los municipios de Colombia con historico de población 1985-2023
    opciones_de_almacenes : dict
        Opciones de los mejores 21 almacenes por departamento {divipol: pd.DataFrame}
    """
    # Cargar los datos
    matriz_de_costos = pd.read_csv("data/matriz-de-costos.csv", index_col=0)
    matriz_de_distancias = pd.read_csv("data/matriz-de-distancias.csv", index_col=0)
    # pasar los nombres de las columnas a enteros
    matriz_de_distancias.columns = matriz_de_distancias.columns.astype(int)
    matriz_de_distancias.index = matriz_de_distancias.index.astype(int)
    # Convertir las medidas de metros a kilometros
    matriz_de_distancias = matriz_de_distancias / 1000
    municipios = pd.read_csv("data/municipios.csv", index_col=3)
    opciones_de_almacenes = {}
    xls = pd.ExcelFile("data/opciones-de-almacenes.xlsx")
    for sheet_name in xls.sheet_names:
        # if the sheet is not empty
        if not xls.parse(sheet_name).empty:
            opciones_de_almacenes[sheet_name] = pd.read_excel(xls, sheet_name)
    return (
        matriz_de_costos,
        matriz_de_distancias,
        municipios,
        opciones_de_almacenes,
    )


def alistar_datos_completos(
    matriz_de_costos,
    matriz_de_distancias,
    municipios,
    opciones_de_almacenes,
    comida_per_capita,
    densidad_de_alimentos,
):
    """
    Alistar los datos que de los que se tiene información completa, es decir,
    los municipios para los cuales se tienen datos en la matriz de costos

    Parametros
    ----------
    matriz_de_costos : pd.DataFrame
        Matriz de costos de transporte entre municipios sacados del SiceTac
    matriz_de_distancias : pd.DataFrame
        Matriz de distancias entre todos los municipios de Colombia por carretera con OpenStreetMap
    municipios : pd.DataFrame
        Información de los municipios de Colombia con historico de población 1985-2023
    opciones_de_almacenes : dict
        Opciones de los mejores 21 almacenes por departamento {divipol: pd.DataFrame}
    comida_per_capita : float
        Cantidad de comida necesaria por persona
    densidad_de_alimentos : float
        Densidad de los alimentos

    Returns
    -------
    matriz_de_costos_final : pd.DataFrame
        Matriz de costos de transporte entre municipios con información completa
    matriz_de_distancias_final : pd.DataFrame
        Matriz de distancias entre todos los municipios de Colombia con información completa
    municipios_final : pd.DataFrame
        Información de los municipios de Colombia con historico de población 1985-2023
         con información completa
    seleccion_de_almacenes_final : pd.DataFrame
        Selección de los almacenes que cumplen con la demanda de almacenamiento

    Proceso
    -------
    # Matriz de costos
    1. Rectificar que no existan indices o nombres de columna duplicados
    2. Rectificar que no existan valores nulos
    3. Rectificar que no existan valores negativos
    4. Rectificar que no existan valores iguales a cero fuera de la diagonal principal
    5. Rectificar que la matriz sea simétrica
    6. Rectificar que la diagonal principal sea cero
    # Matriz de distancias
    1. Eliminar filas y columnas que no estén en la matriz de costos
    2. Rectificar que no existan indices o nombres de columna duplicados
    3. Rectificar que no existan valores nulos
        3.1 Si existen valores nulos, eliminar la fila
        3.2 Rectificar que las las columnas tengan los mismos nombres que las filas
    4. Rectificar que no existan valores negativos
    5. Rectificar que no existan valores iguales a cero fuera de la diagonal principal
    6. Rectificar que la matriz sea simétrica
    7. Rectificar que la diagonal principal sea cero
    8. utilizar el valor máximo entre la distancia entre los municipios
      y la distancia en línea recta
    # Municipios
    1. Eliminar filas que no estén en la matriz de costos
    2. tomar solo las columnas de interés
        a. divipola [index]
        b. nombre del municipio [municipio]
        c. nombre del departamento [departamento]
        d. latitud [lat]
        e. longitud [lon]
        f. población [1985-2023]
    # Opciones de almacenes
    1. Eliminar las opciones que no estén en la matriz de costos
    2. Encontrar por municipio que tantos m2 de almacenamiento se necesitan
    3. Revisar si existe un almacen que cumpla la demanda por un factor de 1.5
        3.1. Si no existe, revisar si la suma de los almacenes cumple la demanda
          por un factor de 1.5
            3.1.1. Entre los almacenes cumplen más de la demanda, ordenar los
            almacenes por almacenamiento
                   de mayor a menor y sumar los primeros hasta cumplir la demanda
                     y crear un nuevo almacen
                   con la suma de almacenamiento y la suma de costos
        3.2. Si no existe, no reportar el municipio
    4. Rankear los precios de los almacenes
    5. Rankear la capacidad de los almacenes
    6. Calcular (Rankeo de precios * 0.2 + Rankeo de capacidad * 0.8)
    7. Seleccionar el mejor almacen por departamento
    8. Retornar una lista con los datos [divipol, location -> ubicacion, area, price -> precio]
    """
    # Matriz de costos
    matriz_de_costos_final = procesar_matriz_de_costos_completos(matriz_de_costos)
    print("Matriz de costos completada")

    # Matriz de distancias
    matriz_de_distancias_final = procesar_matriz_de_distancias_completas(
        matriz_de_distancias, municipios, matriz_de_costos_final
    )
    print("Matriz de distancias completada")

    # Municipios
    municipios_final = procesar_municipios_completos(municipios, matriz_de_costos_final)
    print("Municipios completados")

    # Opciones de almacenes
    seleccion_de_almacenes_final = procesar_opciones_de_almacenes(
        opciones_de_almacenes,
        comida_per_capita,
        densidad_de_alimentos,
        matriz_de_costos_final,
        municipios_final,
    )
    print("Opciones de almacenes completadas")
    # hacer todos df
    matriz_de_costos_final = pd.DataFrame(matriz_de_costos_final)
    matriz_de_distancias_final = pd.DataFrame(matriz_de_distancias_final)
    municipios_final = pd.DataFrame(municipios_final)
    seleccion_de_almacenes_final = pd.DataFrame(seleccion_de_almacenes_final)
    return (
        matriz_de_costos_final,
        matriz_de_distancias_final,
        municipios_final,
        seleccion_de_almacenes_final,
    )


def procesar_opciones_de_almacenes(
    opciones_de_almacenes,
    comida_per_capita,
    densidad_de_alimentos,
    matriz_de_costos_final,
    municipios_final,
):
    """
    Procesar las opciones de almacenes para seleccionar el mejor almacen por departamento
    """
    opciones_de_almacenes_final = pd.DataFrame(
        columns=["divipol", "ubicacion", "area", "capacidad", "precio"]
    )
    for divipol, opciones in opciones_de_almacenes.items():
        divipol = int(divipol)
        # 1. Eliminar las opciones que no estén en la matriz de costos
        if divipol not in matriz_de_costos_final.index:
            print(f"     No se encontró información para el municipio {divipol}")
            continue
            # 2. Encontrar por municipio que tantos m2 de almacenamiento se necesitan
        demanda = municipios_final.loc[divipol, "2023"] * comida_per_capita
        # 3. Revisar si existe un almacen que cumpla la demanda por un factor de 1.5
        opciones["capacidad"] = (
            opciones["area"] * densidad_de_alimentos * 5
        )  # 5 metros de altura
        opciones["cumple_demanda"] = opciones["capacidad"] >= demanda * 1.5

        opciones = opciones[opciones["cumple_demanda"]].copy()
        if opciones["cumple_demanda"].sum() == 0:
            print(
                f"     No se encontró un almacen que cumpla la demanda para {divipol}"
            )
            continue

        if demanda == 0:
            print(f"     La demanda para el municipio {divipol} es cero")
            continue

        # 4. Rankear los precios de los almacenes
        opciones["rank_precio"] = opciones["price"].rank(ascending=True)
        # 5. Rankear la capacidad de los almacenes
        opciones["rank_capacidad"] = opciones["capacidad"].rank(ascending=False)
        # 6. Calcular (Rankeo de precios * 0.2 + Rankeo de capacidad * 0.8)
        opciones["rank_total"] = (
            opciones["rank_precio"] * 0.2 + opciones["rank_capacidad"] * 0.8
        )
        # 7. Seleccionar el mejor almacen por departamento
        opciones = opciones.sort_values("rank_total", ascending=True)
        opcion_a_escoger = {
            "divipol": divipol,
            "ubicacion": opciones.iloc[0]["location"],
            "area": opciones.iloc[0]["area"],
            "capacidad": opciones.iloc[0]["capacidad"],
            "precio": opciones.iloc[0]["price"],
        }
        opcion_a_escoger = pd.DataFrame(opcion_a_escoger, index=[0])
        warnings.catch_warnings()
        warnings.simplefilter("ignore", category=FutureWarning)
        opciones_de_almacenes_final = pd.concat(
            [opciones_de_almacenes_final, opcion_a_escoger]
        )
    # set divipol as index
    opciones_de_almacenes_final = opciones_de_almacenes_final.set_index("divipol")

    return opciones_de_almacenes_final


def procesar_municipios_completos(municipios, matriz_de_costos_final):
    """
    Procesar los municipios completos"""
    # 1. Eliminar filas que no estén en la matriz de costos
    print(f"     Se eliminaron {len(municipios) - len(matriz_de_costos_final)} filas")
    municipios = municipios.loc[matriz_de_costos_final.index]
    # 2. tomar solo las columnas de interés
    columnas_de_interes = ["municipio", "departamento", "lat", "lon"] + [
        str(x) for x in range(1985, 2024)
    ]
    municipios_final = municipios[columnas_de_interes]
    # para 27086 tomar los mismos valores que 27493 para la población 1985 | ... | 2023
    if 27086 in municipios_final.index:
        municipios_final.loc[27086, "1985":"2023"] = municipios_final.loc[27495, "1985":"2023"]

    return municipios_final


def procesar_matriz_de_distancias_completas(
    matriz_de_distancias, municipios, matriz_de_costos_final
):
    """
    Procesar la matriz de distancias completa"""
    # 1. Eliminar filas y columnas que no estén en la matriz de costos
    matriz_de_distancias = matriz_de_distancias.loc[
        matriz_de_costos_final.index, matriz_de_costos_final.index
    ]
    # 2. Rectificar que no existan indices o nombres de columna duplicados
    matriz_de_distancias = matriz_de_distancias.loc[
        ~matriz_de_distancias.index.duplicated(keep="first")
    ]
    matriz_de_distancias = matriz_de_distancias.loc[
        ~matriz_de_distancias.columns.duplicated(keep="first")
    ]
    # 3. Rectificar que no existan valores nulos
    if matriz_de_distancias.isnull().sum().sum() > 0:
        assert matriz_de_distancias.isnull().sum().sum() == 0, "Existen valores nulos"
        matriz_de_distancias = matriz_de_distancias.dropna()
        matriz_de_distancias = matriz_de_distancias.loc[
            matriz_de_distancias.index, matriz_de_distancias.columns
        ]
        print("     Se eliminaron los valores nulos")
        # 4. Rectificar que no existan valores negativos
    assert (matriz_de_distancias < 0).sum().sum() == 0, "Existen valores negativos"
    # 5. Rectificar que no existan valores iguales a cero fuera de la diagonal principal
    assert (
        matriz_de_distancias.values[~np.eye(matriz_de_distancias.shape[0], dtype=bool)]
        == 0
    ).sum() == 0, "Existen valores iguales a cero fuera de la diagonal principal"
    # 6. Rectificar que la matriz tenga simetría
    assert len(matriz_de_distancias) == len(
        matriz_de_distancias.columns
    ), "La matriz no es simétrica"
    # 7. Rectificar que la diagonal principal sea cero
    assert (
        np.diag(matriz_de_distancias) == 0
    ).all(), "La diagonal principal no es cero"
    # 8. utilizar el valor máximo entre la distancia entre los municipios
    # y la distancia en línea recta
    correccion = 0
    for i in matriz_de_distancias.index:
        for j in matriz_de_distancias.columns:
            dato_actual = matriz_de_distancias.loc[i, j]
            distancia = geopy.distance.distance(
                (municipios.loc[i, "lat"], municipios.loc[i, "lon"]),
                (municipios.loc[j, "lat"], municipios.loc[j, "lon"]),
            ).km
            if dato_actual < distancia:
                matriz_de_distancias.loc[i, j] = distancia
                correccion += 1
    if correccion > 0:
        print(f"     Se corrigieron {correccion} valores por distancia en línea recta")
    return matriz_de_distancias


def procesar_matriz_de_costos_completos(matriz_de_costos):
    """
    Procesar la matriz de costos completa"""
    # 1. Rectificar que no existan indices o nombres de columna duplicados
    matriz_de_costos = matriz_de_costos.loc[
        ~matriz_de_costos.index.duplicated(keep="first")
    ]
    matriz_de_costos = matriz_de_costos.loc[
        ~matriz_de_costos.columns.duplicated(keep="first")
    ]
    # 2. Rectificar que no existan valores nulos
    assert matriz_de_costos.isnull().sum().sum() == 0, "Existen valores nulos"
    # 3. Rectificar que no existan valores negativos
    assert (matriz_de_costos < 0).sum().sum() == 0, "Existen valores negativos"
    # 4. Rectificar que no existan valores iguales a cero fuera de la diagonal principal
    assert (
        matriz_de_costos.values[~np.eye(matriz_de_costos.shape[0], dtype=bool)] == 0
    ).sum() == 0, "Existen valores iguales a cero fuera de la diagonal principal"
    # 5. Rectificar que la matriz tenga simetría
    assert len(matriz_de_costos) == len(
        matriz_de_costos.columns
    ), "La matriz no es simétrica"
    # 6. Rectificar que la diagonal principal sea cero
    assert (np.diag(matriz_de_costos) == 0).all(), "La diagonal principal no es cero"
    return matriz_de_costos


def procesar_datos_completos(comida_per_capita, densidad_de_alimentos):
    """
    Procesar los datos completos"""
    print("Procesando los DATOS COMPLETOS")
    # Revisar si ya se procesaron los datos
    datos_a_procesar = [
        "data/datos_completos/matriz-de-costos.csv",
        "data/datos_completos/matriz-de-distancias.csv",
        "data/datos_completos/municipios.csv",
        "data/datos_completos/almacenes.csv",
    ]
    if all([os.path.exists(dato) for dato in datos_a_procesar]):
        print("Los datos ya fueron procesados")
        return
    # Cargar los datos
    matriz_de_costos, matriz_de_distancias, municipios, opciones_de_almacenes = (
        cargar_datos()
    )
    # Alistar los datos completos
    matriz_de_costos, matriz_de_distancias, municipios, opciones_de_almacenes = (
        alistar_datos_completos(
            matriz_de_costos,
            matriz_de_distancias,
            municipios,
            opciones_de_almacenes,
            comida_per_capita,
            densidad_de_alimentos,
        )
    )

    # Guardar los datos
    # Matriz de costos en pesos = matriz_de_costos * matriz_de_distancias
    if matriz_de_costos is not None:
        guardar_datos_completos(
            matriz_de_costos, matriz_de_distancias, municipios, opciones_de_almacenes
        )


def guardar_datos_completos(
    matriz_de_costos, matriz_de_distancias, municipios, opciones_de_almacenes
):
    """
    Guardar los datos procesados"""
    matriz_de_costos_en_pesos = pd.DataFrame(
        matriz_de_costos.values * matriz_de_distancias.values,
        index=matriz_de_costos.index,
        columns=matriz_de_costos.columns,
    )
    matriz_de_costos_en_pesos.to_csv("data/datos_completos/matriz-de-costos.csv")
    matriz_de_distancias.to_csv("data/datos_completos/matriz-de-distancias.csv")
    municipios.to_csv("data/datos_completos/municipios.csv")
    opciones_de_almacenes.to_csv("data/datos_completos/almacenes.csv")


def alistar_datos_imperfectos(
    matriz_de_costos: pd.DataFrame | None,
    matriz_de_distancias: pd.DataFrame | None,
    municipios: pd.DataFrame | None,
    seleccion_de_almacenes: pd.DataFrame | None,
):
    """
    Alistar los datos que de los que se tiene información incompleta, es decir,
    Los municipios para los cuales existe vía terrestre entre ellos, pero no se tiene
    información de costos de transporte.

    Parametros
    ----------
    matriz_de_costos : pd.DataFrame
        Matriz de costos de transporte entre municipios sacados del SiceTac
    matriz_de_distancias : pd.DataFrame
        Matriz de distancias entre todos los municipios de Colombia por carretera con OpenStreetMap
    municipios : pd.DataFrame
        Información de los municipios de Colombia con historico de población 1985-2023
    seleccion_de_almacenes : pd.DataFrame
        Selección de los almacenes que cumplen con la demanda de almacenamiento
    comida_per_capita : float
        Cantidad de comida necesaria por persona
    densidad_de_alimentos : float
        Densidad de los alimentos

    Returns
    -------
    matriz_de_costos_final : pd.DataFrame
        Matriz de costos de transporte entre municipios con información completa
        + promedio para los municipios incompletos
    matriz_de_distancias_final : pd.DataFrame
        Matriz de distancias entre todos los municipios ajustado a los que tienen ruta terrestre
    municipios_final : pd.DataFrame
        Información de los municipios de Colombia con historico de población 1985-2023
    seleccion_de_almacenes_final : pd.DataFrame
        Selección de los almacenes que cumplen con la demanda de almacenamiento

    Proceso
    -------
    # Matriz de distancias
    1. Eliminar valores nulos (valores que no tienen ruta terrestre)
    [0 fuera de la diagonal principal]
    2. Filtrar las columnas correspondientes a las filas, haciendo la matriz cuadrada
    3. Escoger el máximo entre la distancia en línea recta y la distancia por carretera
    4. Rectificar que no existan valores nulos
    5. Rectificar que no existan valores negativos
    6. Rectificar que no existan valores iguales a cero fuera de la diagonal principal
    # Matriz de costos
    1. Leer la matriz de costos completa
        1.1. añadir las filas y columnas que falten para ser la matriz de distancias
    2. añadir los valores promedio para los municipios que no tienen información por filas con datos
    3. añadir los valores promedio para los municipios que no tienen información por columnas
    4. Rectificar que no existan valores nulos
    5. Rectificar que no existan valores negativos
    6. Rectificar que no existan valores iguales a cero fuera de la diagonal principal
    7. Rectificar que la diagonal principal sea cero
    # Municipios
    1. Eliminar filas que no estén en la matriz de distancias
    2. tomar solo las columnas de interés
        a. divipola [index]
        b. nombre del municipio [municipio]
        c. nombre del departamento [departamento]
        d. latitud [lat]
        e. longitud [lon]
        f. población [1985-2023]
    # Almacenes
    1. Retornar la selección de almacenes de la información completa
    """
    matriz_de_distancias = pd.DataFrame(matriz_de_distancias)
    matriz_de_costos = pd.DataFrame(matriz_de_costos)
    municipios = pd.DataFrame(municipios)
    seleccion_de_almacenes = pd.DataFrame(seleccion_de_almacenes)

    #### PROCESO ####
    matriz_de_distancias_final = procesar_matriz_de_distancias_imperfectas(
        matriz_de_distancias, municipios
    )
    print("Matriz de distancias completada")

    matriz_de_costos_final = procesar_matriz_de_costos_imperfectos(
        matriz_de_costos, matriz_de_distancias_final
    )
    print("Matriz de costos completada")

    municipios_final = procesar_municipios_completos(
        municipios, matriz_de_distancias_final
    )
    print("Municipios completados")

    seleccion_de_almacenes_final = seleccion_de_almacenes
    print("Opciones de almacenes completadas")

    return (
        matriz_de_costos_final,
        matriz_de_distancias_final,
        municipios_final,
        seleccion_de_almacenes_final,
    )


def procesar_matriz_de_distancias_imperfectas(
    matriz_de_distancias: pd.DataFrame, municipios: pd.DataFrame
):
    """
    Procesar la matriz de distancias imperfecta"""
    # Matriz de distancias
    # 1. Eliminar valores nulos (valores que no tienen ruta terrestre)
    #  [0 fuera de la diagonal principal]
    print(
        f"    Cantidad de Municipios que demuestran inconsistencia en via terrestre \
              {matriz_de_distancias.iloc[:,0].isnull().sum()}"
    )

    matriz_de_distancias = matriz_de_distancias.replace(0, np.nan)
    # 1.1 hacer la diagonal principal cero
    matriz_de_distancias = pd.DataFrame(
        np.where(np.eye(len(matriz_de_distancias)), 0, matriz_de_distancias),
        index=matriz_de_distancias.index,
        columns=matriz_de_distancias.columns,
    )
    matriz_de_distancias = matriz_de_distancias.dropna(
        subset=matriz_de_distancias.columns[0]
    )
    # 2. Filtrar las columnas correspondientes a las filas, haciendo la matriz cuadrada
    matriz_de_distancias = matriz_de_distancias.loc[
        :, matriz_de_distancias.index.to_list()
    ]
    print(
        f"    Cantidad de valores no existentes: \
            {matriz_de_distancias.isnull().sum().sum()} \
                previo a ajuste de distancias"
    )
    # 3. Escoger el máximo entre la distancia en línea recta y la distancia por carretera
    cuenta_ajustes = 0
    cuenta_ceros = 0
    for i in matriz_de_distancias.index:
        for j in matriz_de_distancias.columns:
            if i == j:
                matriz_de_distancias.loc[i, j] = 0
            elif pd.isnull(matriz_de_distancias.loc[i, j]):
                distancia_linea_recta = geopy.distance.distance(
                    (municipios.loc[i, "lat"], municipios.loc[i, "lon"]),
                    (municipios.loc[j, "lat"], municipios.loc[j, "lon"]),
                ).km
                matriz_de_distancias.loc[i, j] = distancia_linea_recta
                cuenta_ajustes += 1
            else:
                distancia_real = matriz_de_distancias.loc[i, j]
                distancia_linea_recta = geopy.distance.distance(
                    (municipios.loc[i, "lat"], municipios.loc[i, "lon"]),
                    (municipios.loc[j, "lat"], municipios.loc[j, "lon"]),
                ).km
                if distancia_real < distancia_linea_recta:
                    matriz_de_distancias.loc[i, j] = distancia_linea_recta
                    cuenta_ajustes += 1
                if distancia_real == 0:
                    cuenta_ceros += 1
    print(
        f"    Cantidad de valores no existentes: {matriz_de_distancias.isnull().sum().sum()}\
              posterior a ajuste de distancias"
    )
    print(f"    Se ajustaron {cuenta_ajustes} distancias")
    if matriz_de_distancias.isnull().sum().sum() < 0:
        print("    Se ajustó la matriz de distancias de manera satisfactoria")
    else:
        print("    No se ajustó la matriz de distancias de manera satisfactoria")

    print(
        f"    Se encontraron {cuenta_ceros} valores iguales a cero fuera de la diagonal principal"
    )

    # 4. Rectificar que no existan valores nulos
    assert matriz_de_distancias.isnull().sum().sum() == 0, "Existen valores nulos"
    # 5. Rectificar que no existan valores negativos
    assert (matriz_de_distancias < 0).sum().sum() == 0, "Existen valores negativos"

    return matriz_de_distancias


def procesar_matriz_de_costos_imperfectos(
    matriz_de_costos: pd.DataFrame,
    matriz_de_distancias: pd.DataFrame,
):
    """
    Procesar la matriz de costos imperfecta"""
    # 1. Leer la matriz de costos completa
    # 1.1 añadir las filas y columnas que falten para ser la matriz de distancias
    matriz_de_costos.index = matriz_de_costos.index.astype(int)
    matriz_de_costos.columns = matriz_de_costos.columns.astype(int)

    matriz_de_costos_imperfectos = matriz_de_costos.reindex_like(matriz_de_distancias)

    # 2. añadir los valores promedio para los municipios que no
    # tienen información por filas con datos
    # primero por filas
    matriz_de_costos_imperfectos = matriz_de_costos_imperfectos.fillna(
        matriz_de_costos_imperfectos.mean(axis=0),
        axis=0,
    )
    # despues por columnas
    matriz_de_costos_imperfectos = matriz_de_costos_imperfectos.fillna(
        matriz_de_costos_imperfectos.mean(axis=1)
    )
    # hacer la diagonal principal cero
    matriz_de_costos_imperfectos = pd.DataFrame(
        np.where(
            np.eye(len(matriz_de_costos_imperfectos)), 0, matriz_de_costos_imperfectos
        ),
        index=matriz_de_costos_imperfectos.index,
        columns=matriz_de_costos_imperfectos.columns,
    )
    # 4. Rectificar que no existan valores nulos
    assert (
        matriz_de_costos_imperfectos.isnull().sum().sum() == 0
    ), "Existen valores nulos"
    # 5. Rectificar que no existan valores negativos
    assert (
        matriz_de_costos_imperfectos < 0
    ).sum().sum() == 0, "Existen valores negativos"
    return matriz_de_costos_imperfectos


def guardar_datos_imperfectos(
    matriz_de_costos, matriz_de_distancias, municipios, opciones_de_almacenes
):
    """
    Guardar los datos procesados"""
    matriz_de_costos_en_pesos = pd.DataFrame(
        matriz_de_costos.values * matriz_de_distancias.values,
        index=matriz_de_costos.index,
        columns=matriz_de_costos.columns,
    )
    matriz_de_costos_en_pesos.to_csv("data/datos_imperfectos/matriz-de-costos.csv")
    matriz_de_distancias.to_csv("data/datos_imperfectos/matriz-de-distancias.csv")
    municipios.to_csv("data/datos_imperfectos/municipios.csv")
    opciones_de_almacenes.to_csv("data/datos_imperfectos/almacenes.csv")


def procesar_datos_imperfectos():
    """
    Procesar los datos imperfectos"""
    print("Procesando los DATOS IMPERFECTOS")
    # Revisar si ya se procesaron los datos
    datos_a_procesar = [
        "data/datos_imperfectos/matriz-de-costos.csv",
        "data/datos_imperfectos/matriz-de-distancias.csv",
        "data/datos_imperfectos/municipios.csv",
        "data/datos_imperfectos/almacenes.csv",
    ]
    if all([os.path.exists(dato) for dato in datos_a_procesar]):
        print("Los datos ya fueron procesados")
        return
    # Cargar los datos
    matriz_de_costos, matriz_de_distancias, municipios, opciones_de_almacenes = (
        cargar_datos()
    )
    del opciones_de_almacenes
    # Alistar los datos incompletos
    seleccion_de_almacenes = pd.read_csv(
        "data/datos_completos/almacenes.csv", index_col=0
    )
    matriz_de_costos, matriz_de_distancias, municipios, seleccion_de_almacenes = (
        alistar_datos_imperfectos(
            matriz_de_costos,
            matriz_de_distancias,
            municipios,
            seleccion_de_almacenes,
        )
    )

    # Guardar los datos
    # Matriz de costos en pesos = matriz_de_costos * matriz_de_distancias
    if matriz_de_costos is not None:
        guardar_datos_imperfectos(
            matriz_de_costos, matriz_de_distancias, municipios, seleccion_de_almacenes
        )
