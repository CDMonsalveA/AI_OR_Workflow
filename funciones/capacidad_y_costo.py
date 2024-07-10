"""capacidad_y_costo()
2. Determinar las capacidades y costos de almacenamiento de alimentos
en cada municipio utilizando los datos del pronóstico, los datos
abiertos y consideraciones de los analístas.

en esta sección, se busca encontrar la capacidad y el costo de almacenamiento
de alimentos para cada municipio, ya se tiene en los datos de almacenes la
capacidad y costo mensual de algunos municipios, para los cuales no se puede
alquilar un almacén, se asume que la mejor estratégia posible es construir
naves industriales, los tipos de almacenes son (todos de 5m de altura):
    tipo | capacidad (toneladas/semana) | costo (COP/semana)
    1    | 1074                         | 3111202.75
    2    | 2418                         | 4804980.75
por municipio se puede construir más de un tipo de almacén, se busca minimizar
el costo de construcción y satisfacer la demanda de alimentos para la población,
sabiendo que la demanda de alimentos es de 0.87617 kg por persona.

Los datos de arrendamiento de almacenes ya satisfacen la demanda de alimentos
para la población del municipio, por lo que no se necesita construir almacenes,
además se asume un factor de seguridad de 1.5 para la capacidad de los almacenes
ya que se asume que la demanda de alimentos no es constante y puede variar.

el modelo de optimización que se va a utilizar es el siguiente:
  SETS:
      i = {1, 2, ..., n} conjunto de municipios
      j = {1, 2} conjunto de tipos de almacenes
  PARAMETERS:
      d_i = demanda de alimentos en el municipio i
          d_i = poblacion_i * comida_per_capita
      c_j = capacidad de almacenamiento del tipo j
      costo_j = costo de construcción del tipo j
  VARIABLES:
      x_ij = cantidad de almacenes del tipo j en el municipio i
  OBJECTIVE FUNCTION:
      min sum(i, j) costo_j * x_ij
  CONSTRAINTS:
      sum(j) c_j * x_ij >= d_i | i = {1, 2, ..., n}
      x_ij >= 0 | i = {1, 2, ..., n}, j = {1, 2}
      x_ij = integer | i = {1, 2, ..., n}, j = {1, 2}


proceso general:
  1. leer los datos de los almacenes
  2. leer los datos del pronóstico poblacional de los municipios para 2034
  3. calcular la demanda de alimentos para cada municipio
  5. resolver el problema de optimización
  6. guardar los resultados en un archivo csv en
      resultados/tablas/capacidad_y_costo.csv"""
import os
import warnings

import pandas as pd
import pulp as pl



def tipos_de_almacenes():
    data = {
        1: {"capacidad": 1074, "costo": 3111202.75},
        2: {"capacidad": 2418, "costo": 4804980.75},
    }
    return pd.DataFrame(data).T


def demanda_de_alimentos(poblacion: pd.Series, comida_per_capita: float) -> pd.Series:
    return pd.to_numeric(poblacion) * comida_per_capita * 7 * 1.5


def get_demanda_completo_e_imperfecto(comida_per_capita: float):
    poblacion_completo = pd.read_csv(
        "resultados/tablas/pronostico_poblacional/datos_completos.csv", index_col=0
    )
    poblacion_imperfecto = pd.read_csv(
        "resultados/tablas/pronostico_poblacional/datos_imperfectos.csv", index_col=0
    )

    demanda_completa = demanda_de_alimentos(
        poblacion_completo["Poblacion_2034"], comida_per_capita
    )
    demanda_imperfecta = demanda_de_alimentos(
        poblacion_imperfecto["Poblacion_2034"], comida_per_capita
    )

    data = {
        "demanda_completa": demanda_completa,
        "demanda_imperfecta": demanda_imperfecta,
    }
    return data


def pl_capacidad_y_costos(
    d_i: pd.Series, c_j: pd.Series, costo_j: pd.Series, id_data: str
):
    """
    Soluciona el problema de optimización de capacidad y costos de almacenamiento
    de alimentos en cada municipio.

    Parameters
    ----------
    d_i : pd.Series
        demanda semanal de alimentos en cada municipio
    c_j : pd.Series
        capacidad de almacenamiento de cada tipo de almacén en toneladas
    costo_j : pd.Series
        costo de construcción de cada tipo de almacén en COP/semana

    Returns
    -------
    solucion : pd.DataFrame
        cantidad de almacenes de cada tipo en cada municipio
            solucion.columns = [(x_ij),capacidad, costo] en donde x_ij es un
                                        tuple con la cantidad de almacenes
                                        de cada tipo
            solucion.index = d_i.index

    Problema de optimización
    ------------------------

    SETS:
        i = {1, 2, ..., n} conjunto de municipios
        j = {1, 2} conjunto de tipos de almacenes
    PARAMETERS:
        d_i = demanda de alimentos en el municipio i
        c_j = capacidad de almacenamiento del tipo j
        costo_j = costo de construcción del tipo j
    VARIABLES:
        x_ij = cantidad de almacenes del tipo j en el municipio i
    OBJECTIVE FUNCTION:
        min sum(i, j) costo_j * x_ij
    CONSTRAINTS:
        sum(j) c_j * x_ij >= d_i | i = {1, 2, ..., n}
        x_ij >= 0 | i = {1, 2, ..., n}, j = {1, 2}
        x_ij = integer | i = {1, 2, ..., n}, j = {1, 2}
    """
    warnings.filterwarnings("ignore", category=UserWarning)
    I = d_i.index
    J = c_j.index

    # Crear el problema de optimización
    prob = pl.LpProblem("capacidad_y_costo", pl.LpMinimize)

    # Crear las variables
    x = pl.LpVariable.dicts("x", (I, J), lowBound=0, cat="Integer")

    # Crear la función objetivo
    prob += pl.lpSum([costo_j[j] * x[i][j] for i in I for j in J])

    # Crear las restricciones
    for i in I:
        prob += pl.lpSum([c_j[j] * x[i][j] for j in J]) >= d_i[i]

    # Resolver el problema
    prob.solve(
        solver=pl.PULP_CBC_CMD(
            logPath=f"resultados/logs/2. capacidad_y_costo/{id_data}.log",
            threads=os.cpu_count(),
        )
    )

    # Crear el dataframe de la solución
    solucion = pd.DataFrame(index=I, columns=["capacidad", "precio", "x_ij"])
    for i in I:
        solucion.loc[i, "capacidad"] = sum([c_j[j] * x[i][j].varValue for j in J])
        solucion.loc[i, "precio"] = sum([costo_j[j] * x[i][j].varValue for j in J])
        solucion.loc[i, "x_ij"] = [x[i][j].varValue for j in J]

    return solucion


def capacidad_y_costo(comida_per_capita):
    archivos_a_crearse = [
        "resultados/tablas/capacidad_y_costo/solucion-pl-demanda_completa.csv",
        "resultados/tablas/capacidad_y_costo/solucion-pl-demanda_imperfecta.csv",
        "resultados/tablas/capacidad_y_costo/demanda_completa.csv",
        "resultados/tablas/capacidad_y_costo/demanda_imperfecta.csv",
    ]
    if all([os.path.exists(archivo) for archivo in archivos_a_crearse]):
        print("\nLa capacidad y costos ya fueron calculados", end="\n")
        return

    demandas = get_demanda_completo_e_imperfecto(comida_per_capita)
    naves = tipos_de_almacenes()

    for id_data, data in demandas.items():
        print(f"\nResolviendo el problema de optimización para {id_data}", end="\n")
        solucion = pl_capacidad_y_costos(
            data, naves["capacidad"], naves["costo"], id_data
        )
        solucion.to_csv(
            f"resultados/tablas/capacidad_y_costo/solucion-pl-{id_data}.csv"
        )

        bodegas_para_arrendar = pd.read_csv(
            "data/datos_completos/almacenes.csv", index_col=0
        )
        # hacer la columna precio /4 para pasar a precio semanal
        bodegas_para_arrendar["precio"] = bodegas_para_arrendar["precio"] / 4
        bodegas_para_arrendar["x_ij"] = "Arrendar"
        # reindexar las bodegas para arrendar
        bodegas_para_arrendar = bodegas_para_arrendar.reindex_like(solucion)
        # escoger la opción de menor costo entre construir y arrendar
        cuenta_arriendos = 0
        for i in solucion.index:
            if pd.to_numeric(solucion.loc[i, "precio"]) > pd.to_numeric(
                bodegas_para_arrendar.loc[i, "precio"]
            ):
                solucion.loc[i, "precio"] = bodegas_para_arrendar.loc[i, "precio"]
                solucion.loc[i, "capacidad"] = bodegas_para_arrendar.loc[i, "capacidad"]
                solucion.loc[i, "x_ij"] = bodegas_para_arrendar.loc[i, "x_ij"]
                cuenta_arriendos += 1
        print(f"Se arrendaron {cuenta_arriendos} bodegas para {id_data}")

        solucion.to_csv(f"resultados/tablas/capacidad_y_costo/{id_data}.csv")
        print(
            f"Guardando los resultados en resultados/tablas/capacidad_y_costo/{id_data}.csv"
        )
