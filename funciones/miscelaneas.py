"""Funciones miscelaneas para crear la estructura de archivos, entre otras cosas
"""
import os

def crear_estructura_de_archivos():
    """
    definición de la estructura de archivos

    carpeta_raiz
        /data
            matriz-de-costos.csv (COP/(KM)) *
            matriz-de-distancias.csv **
            municipios.csv ** (cód, nombres, lat, lon, e historico de población)
            opciones-de-almacenes.xlsx (sheet_name: divipol del municipio)
            /datos_completos *
                matriz-de-costos.csv (COP)
                matriz-de-distancias.csv (KM)
                municipios.csv (cód, nombres, lat, lon, e historico de población)
                almacenes.csv (divipol, ubicacion, area, capacidad, precio) [Capacidad en Toneladas]
            /datos_imperfectos **
        /funciones
            funciones.py
        /resultados
        1. pronostico_poblacional.csv
        2. capacidad_y_costo.csv
        3. cantidad_de_clusteres.csv
        4. generacion_de_clusteres.csv
        5. solucionar_cflp.csv
            /tablas
                /pronostico_poblacional
                    info-completa.csv
                    info-imperfecta.csv
                /capacidad_y_costo
                    info-completa.csv
                    info-imperfecta.csv
            /graficos
                /pronostico_poblacional
                    info-completa.png
                    info-imperfecta.png
                /capacidad_y_costo
                    info-completa.png
                    info-imperfecta.png
            /mapas
                /completo
                    1. ingenua.png
                    2. sin_clusterizar.png
                    3. clusterizada-k-means.png
                    4. clusterizada-mapa_autoorganizado.png
                    5. clusterizada-agrupamiento_jerarquico.png
                /imperfecto
                    1. ingenua.png
                    2. sin_clusterizar.png
                    3. clusterizada-k-means.png
                    4. clusterizada-mapa_autoorganizado.png
                    5. clusterizada-agrupamiento_jerarquico.png
            /logs
                /2. capacidad_y_costo
                    info-completa.log
                    info-imperfecta.log
                /4. cantidad_de_clusteres
                    info-completa.log
                    info-imperfecta.log
                /6. solucionar_cflp
                    /1. ingenua
                        info-completa.log
                        info-imperfecta.log
                    /2. sin_clusterizar
                        info-completa.log
                        info-imperfecta.log
                    /3. clusterizada
                        /1. k-means
                            /info-completa
                                [Archivo por cluster].log
                            /info-imperfecta
                                [Archivo por cluster].log
                        /2. mapa_autoorganizado
                            /info-completa
                                [Archivo por cluster].log
                            /info-imperfecta
                                [Archivo por cluster].log
                        /3. agrupamiento_jerarquico
                            /info-completa
                                [Archivo por cluster].log
                            /info-imperfecta
                                [Archivo por cluster].log
        * Datos en los que existe información para los municipios
        ** Datos para todos los municipios de colombia
    """
    try:
        # Crear la estructura de archivos
        os.makedirs("data", exist_ok=True)
        os.makedirs("data/datos_completos", exist_ok=True)
        os.makedirs("data/datos_imperfectos", exist_ok=True)
        os.makedirs("funciones", exist_ok=True)
        os.makedirs("resultados", exist_ok=True)
        os.makedirs("resultados/tablas", exist_ok=True)
        os.makedirs("resultados/tablas/pronostico_poblacional", exist_ok=True)
        os.makedirs("resultados/tablas/capacidad_y_costo", exist_ok=True)
        os.makedirs("resultados/tablas/predecir_capacidad_y_costo", exist_ok=True)
        os.makedirs("resultados/tablas/cantidad_de_clusteres", exist_ok=True)
        os.makedirs("resultados/tablas/clusteres", exist_ok=True)
        os.makedirs("resultados/graficos", exist_ok=True)
        os.makedirs("resultados/graficos/pronostico_poblacional", exist_ok=True)
        os.makedirs("resultados/graficos/capacidad_y_costo", exist_ok=True)
        os.makedirs("resultados/mapas", exist_ok=True)
        os.makedirs("resultados/mapas/completo", exist_ok=True)
        os.makedirs("resultados/mapas/imperfecto", exist_ok=True)
        os.makedirs("resultados/logs", exist_ok=True)
        os.makedirs("resultados/logs/2. capacidad_y_costo", exist_ok=True)
        os.makedirs("resultados/logs/4. cantidad_de_clusteres", exist_ok=True)
        os.makedirs("resultados/logs/6. solucionar_cflp", exist_ok=True)
        os.makedirs("resultados/logs/6. solucionar_cflp/1. ingenua", exist_ok=True)
        os.makedirs(
            "resultados/logs/6. solucionar_cflp/2. sin_clusterizar", exist_ok=True
        )
        os.makedirs("resultados/logs/6. solucionar_cflp/3. clusterizada", exist_ok=True)
        os.makedirs(
            "resultados/logs/6. solucionar_cflp/3. clusterizada/1. k-means",
            exist_ok=True,
        )
        os.makedirs(
            "resultados/logs/6. solucionar_cflp/3. clusterizada/2. mapa_autoorganizado",
            exist_ok=True,
        )
        os.makedirs(
            "resultados/logs/6. solucionar_cflp/3. clusterizada/3. agrupamiento_jerarquico",
            exist_ok=True,
        )
    except OSError as e:
        print(f"OS error: {e}")
