"""
# Pronóstico Poblacional
    # Esquema general de la experimentación
    # 1. Seleccionar los datos Historicos teniendo en cuenta su estructura
    #    divipola | 1985 | ... | 2023
    #    en donde los datos pueden existir o no en los años.
    # 2. Por Municipio
    #    2.1. Seleccionar los datos de los años que existen.
    #    2.2. Dividir los datos en entrenamiento y prueba. (80% - 20%)
    #    2.3. Entrenar los modelos.
    #    2.4. Evaluar los modelos.
    #    2.5. Guardar los resultados.
    # 3. Sacar las métricas generales por modelo.
    # 4. Escoger el mejor modelo.
    # 5. Guardar los resultados.
"""
import os
import time

import numpy as np
import pandas as pd

# sklearn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor

# warnings
from sklearn.exceptions import ConvergenceWarning
import warnings

warnings.simplefilter(action="ignore", category=ConvergenceWarning)

def seleccionar_datos_historicos(datos: pd.DataFrame, años: range) -> pd.DataFrame:
    """
    Selecciona los datos históricos de los años que se desean pronosticar.

    Parámetros:
    -----------
    datos: pd.DataFrame
        Datos de los municipios.
    años: range
        Años que se desean pronosticar.

    Retorna:
    --------
    pd.DataFrame
        Datos históricos de los años que se desean pronosticar.
    """
    datos = datos[[str(x) for x in años]]
    datos.columns = datos.columns.astype(int)
    datos = datos.replace(0, np.nan)
    return datos


def definicion_de_modelos_de_regresion(RANDOM_SEED):
    # modelos = {
    #     "Regresión Lineal Múltiple": LinearRegression(),
    #     "Árboles de Regresión": DecisionTreeRegressor(random_state=RANDOM_SEED),
    #     "Máquinas de Vectores de Soporte": SVR(C=1.0, kernel="rbf", gamma="scale"),
    #     "Bosques Aleatorios": RandomForestRegressor(random_state=RANDOM_SEED),
    #     "Redes Neuronales": MLPRegressor(max_iter=1000, random_state=RANDOM_SEED),
    # }
    modelos = {
        "Multiple Linear Regression": LinearRegression(),
        "Regression Tree": DecisionTreeRegressor(
            max_depth=100,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=RANDOM_SEED,
        ),
        "Support Vector Machine": SVR(C=1.0, kernel="rbf", gamma="scale"),
        "Random Forest Regression": RandomForestRegressor(
            n_estimators=10,
            max_depth=5,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=RANDOM_SEED,
        ),
        "Neural Network for population regression": MLPRegressor(
            hidden_layer_sizes=(10, 10, 10, 10, 10),
            activation="logistic",
            solver="adam",
            alpha=0.01,
            batch_size="auto",
            learning_rate="adaptive",
            learning_rate_init=0.01,
            max_iter=1000,
            shuffle=True,
            random_state=RANDOM_SEED,
        ),
    }
    return modelos


def registrar_metricas_de_regresion(
    resultados, divipola, y_test, name, tiempo_inicial, y_pred, tiempo_final
):
    resultados["Modelo"].append(name)
    resultados["Municipio"].append(divipola)
    resultados["R2"].append(r2_score(y_test, y_pred))
    resultados["MAE"].append(mean_absolute_error(y_test, y_pred))
    resultados["MSE"].append(mean_squared_error(y_test, y_pred))
    resultados["RMSE"].append(np.sqrt(mean_squared_error(y_test, y_pred)))
    resultados["tiempo"].append(tiempo_final - tiempo_inicial)

    return resultados


def registrar_metrica_predeterminada(resultados, divipola):
    resultados["Modelo"].append("Promedio")
    resultados["Municipio"].append(divipola)
    resultados["R2"].append(0.9)
    resultados["MAE"].append(0)
    resultados["MSE"].append(0)
    resultados["RMSE"].append(0)
    resultados["tiempo"].append(0)

    return resultados


def entrenamiento_regresion(X_train, X_test, y_train, modelo):
    tiempo_inicial = time.time()
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)

    tiempo_final = time.time()
    return tiempo_inicial, y_pred, tiempo_final


def obtencion_de_metricas_de_regresion(resultados):
    resultados = pd.DataFrame(resultados)
    resultados = resultados[
        resultados["R2"] > 0.8
    ]  # Seleccionar los resultados con R2 mayor a 0.9
    resultados["mejor_modelo"] = resultados.groupby("Municipio")["R2"].transform("max")
    resultados["mejor_modelo_nombre"] = resultados.groupby("Municipio")[
        "Modelo"
    ].transform(lambda x: x[x.idxmax()])

    reporte_de_resultados = resultados.groupby("Modelo").agg(
        {
            "Municipio": "count",
            "mejor_modelo": ["mean", "std"],
            "mejor_modelo_nombre": "first",
            "R2": ["min", "max", "mean", "std"],
            "MAE": ["min", "max", "mean", "std"],
            "MSE": ["min", "max", "mean", "std"],
            "RMSE": ["min", "max", "mean", "std"],
            "tiempo": ["min", "max", "mean", "std"],
        }
    )

    return resultados, reporte_de_resultados


def generar_las_mejores_predicciones_por_municipio(
    id_data, predicciones, resultados, modelos
):
    municipios_con_mejor_modelo = resultados.groupby("Municipio")[
        "mejor_modelo_nombre"
    ].first()
    # Sacar la prediccion de la poblacion en 2034 usando el mejor modelo

    prediccion_2034 = {}
    for divipola, prediccion in predicciones.iterrows():
        prediccion = prediccion.dropna()
        X = prediccion.index.values.reshape(-1, 1)
        y = prediccion.values
        mejor_modelo_para_municipio = municipios_con_mejor_modelo.loc[
            municipios_con_mejor_modelo.index == divipola
        ].values[0]
        if mejor_modelo_para_municipio == "Promedio":
            prediccion_2034[divipola] = y.mean()
            continue
        modelo = modelos[mejor_modelo_para_municipio]
        modelo.fit(X, y)
        prediccion_2034[divipola] = modelo.predict([[2034]])[0]

    prediccion_2034 = pd.Series(prediccion_2034)
    prediccion_2034.name = "Poblacion_2034"
    prediccion_2034 = pd.DataFrame(prediccion_2034)
    prediccion_2034.index.name = "Divipola"
    prediccion_2034.to_csv(f"resultados/tablas/pronostico_poblacional/{id_data}.csv")
    return municipios_con_mejor_modelo


def guardar_metricas_y_reportes_de_regresion(
    id_data, reporte_de_resultados, municipios_con_mejor_modelo
):
    tabla_de_frecuencias_de_mejor_modelo_por_municipio = (
        municipios_con_mejor_modelo.value_counts().to_frame()
    )

    reporte_de_resultados.to_csv(
        f"resultados/tablas/pronostico_poblacional/métricas-{id_data}.csv"
    )
    tabla_de_frecuencias_de_mejor_modelo_por_municipio.to_csv(
        f"resultados/tablas/pronostico_poblacional/{id_data}_frecuencias.csv"
    )


def pronostico_poblacional(RANDOM_SEED):
    """
    # Esquema general de la experimentación
    # 1. Seleccionar los datos Historicos teniendo en cuenta su estructura
    #    divipola | 1985 | ... | 2023
    #    en donde los datos pueden existir o no en los años.
    # 2. Por Municipio
    #    2.1. Seleccionar los datos de los años que existen.
    #    2.2. Dividir los datos en entrenamiento y prueba. (80% - 20%)
    #    2.3. Entrenar los modelos.
    #    2.4. Evaluar los modelos.
    #    2.5. Guardar los resultados.
    # 3. Sacar las métricas generales por modelo.
    # 4. Escoger el mejor modelo.
    # 5. Guardar los resultados.
    """
    archivos_a_generar = [
        "resultados/tablas/pronostico_poblacional/datos_completos.csv",
        "resultados/tablas/pronostico_poblacional/datos_imperfectos.csv",
    ]
    if all([os.path.exists(archivo) for archivo in archivos_a_generar]):
        print("El proceso de pronóstico poblacional ya fue realizado")
        return
    else:
        print("\nIniciando el proceso de pronóstico poblacional", end="\n")

    datos_completos = pd.read_csv("data/datos_completos/municipios.csv", index_col=0)
    datos_imperfectos = pd.read_csv(
        "data/datos_imperfectos/municipios.csv", index_col=0
    )

    bases_de_datos = {
        "datos_completos": datos_completos,
        "datos_imperfectos": datos_imperfectos,
    }

    # 1. Seleccionar los datos Historicos teniendo en cuenta su estructura
    for id_data, datos in bases_de_datos.items():
        print(f"Procesando {id_data}")
        time.sleep(1)
        municipios = seleccionar_datos_historicos(datos, range(1985, 2024))
        predicciones = municipios.copy()

        scaler = StandardScaler()
        municipios = pd.DataFrame(
            scaler.fit_transform(municipios),
            columns=municipios.columns,
            index=municipios.index,
        )

        # 2. Por Municipio
        progreso = 0
        resultados = {
            "Modelo": [],
            "Municipio": [],
            "R2": [],
            "MAE": [],
            "MSE": [],
            "RMSE": [],
            "tiempo": [],
        }
        modelos = definicion_de_modelos_de_regresion(RANDOM_SEED)

        for divipola, municipio in municipios.iterrows():
            municipio = municipio.dropna()
            X = municipio.index.values.reshape(-1, 1)
            y = municipio.values
            if len(y) < 5:
                print(
                    f"El municipio {divipola} no tiene suficientes datos,\
                con {len(y)} años"
                )
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=RANDOM_SEED
            )
            for name, modelo in modelos.items():
                tiempo_inicial, y_pred, tiempo_final = entrenamiento_regresion(
                    X_train, X_test, y_train, modelo
                )
                resultados = registrar_metricas_de_regresion(
                    resultados,
                    divipola,
                    y_test,
                    name,
                    tiempo_inicial,
                    y_pred,
                    tiempo_final,
                )
                # prediccion de la poblacion en 2034 en escalas originales
                progreso += 1
                print(
                    f"Progreso: {progreso/(municipios.shape[0] * len(modelos))*100:0.2f}%",
                    end="\r",
                )
            # añadición de un modelo por defecto que es el promedio de los datos validos con valor R2 = 0.9
            resultados = registrar_metrica_predeterminada(resultados, divipola)

        # 3. Sacar las métricas generales por modelo.
        #     es decir, filtrar los resultados (R2 > 0.9) y
        resultados, reporte_de_resultados = obtencion_de_metricas_de_regresion(
            resultados
        )
        # 4. Escoger el mejor modelo y guardar la predicción
        municipios_con_mejor_modelo = generar_las_mejores_predicciones_por_municipio(
            id_data, predicciones, resultados, modelos
        )

        guardar_metricas_y_reportes_de_regresion(
            id_data, reporte_de_resultados, municipios_con_mejor_modelo
        )
        print(f"Procesamiento de {id_data} terminado")
