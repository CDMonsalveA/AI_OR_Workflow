# AI_OR_Workflow

Artificial Intelligence and Operations Research Workflow is a series of modules that allow the integration of Algorithms and Models from both fields to solve a real-world problem.

## Description

this project contains the basis used in the monograph to achieve the degree of industrial engineer entitled:
> [METHODOLOGICAL DESIGN FOR INTEGRATION OF OPERATIONS RESEARCH AND ARTIFICIAL INTELLIGENCE: SUPPORT FOR LOCATION-ALLOCATION MODELING IN FOOD LOGISTICS](http://hdl.handle.net/11349/92955)

by:

[Cristian David Monsalve Alfonso](mailto:cdmonsalvea@udistrital.edu.co) and [Daniel Alejandro León Castañeda](mailto:danalleonc@udistrital.edu.co)



## Objetivos

El objetivo general de este repositorio es utilizar los datos públicos (ubicados
en la carpeta /data/) de municipios en los que existe información para diseñar
una estrategia para distribuir alimentos en el territorio nacional.

### Objetivos específicos

Existe un objetivo por cada una de las estructuras de sinergia encontradas, estas
se pueden encontrar de manera funcional divididas en los siguientes módulos:

1. pronostico_poblacional
    [IA]1. Determinar por municipio que herramienta es mejor para pronosticar
           la población en 10 años a partir del año actual.
              a. Regresión Lineal Multiple || Multiple Linear Regression.
              b. Arboles de Regresión || Regression Tree.
              c. Máquinas de Vectores de Soporte || Support Vector Machine.
              d. Bosques Aleatorios || Random Forest Regression.
              e. Redes neurales || Deep Learning.
              f. Regresión Tradicional.
2. capacidad_y_costo
    [IO]2. Determinar las capacidades y costos de almacenamiento de alimentos
           en cada municipio utilizando los datos del pronóstico, los datos
           abiertos y consideraciones de los analístas.
3. pronosticar_capacidad_y_costo
    [IA]3. Entrenar un clasificador desde los datos de capacidades y costos
           de almacenamiento por municipio.
              a. Arboles de Decision || Decision Tree.
              b. Análisis Discriminante Lineal || Linear Discriminant Analysis.
              c. Regresión Logística || Logistic Regression.
              d. Máquinas de Vectores de Soporte || Support Vector Machine.
              e. Redes Neurales || Deep Learning.
              f. Análisis de frecuencias. [Aún está en desarrollo la idea]
              La experimentación del caso especial de entrenamiento del modelo de pronóstico se
                puede encontrar en el historial de archivos en la sección 3 del archivo
                <https://github.com/CDMonsalveA/AI_OR_Workflow/blob/Experimentacion-13-07/.backup/test/backup/1%2010CFLP.ipynb>
4. cantidad_de_clusteres
    [IO]4. Proponer una cantidad de clusteres que permitan disminuir el costo
           computacional del algoritmo optimizador y compararlo con los métodos
           tradicionales.
5. generar_clusteres
    [IA]5. Dividir los municipios en clústeres, rectificando que es viable
           satisfacer la demanda de alimentos con la capacidad instalada del
           municipio.
              a. k-means.
              b. Mapa Autoorganizado || Self-Organizing Map.
              c. Agrupamiento Jerárquico || Agglomerative Clustering.
              d. DBSCAN.
              La experimentación del caso especial de entrenamiento del modelo de pronóstico se
                puede encontrar en el historial de archivos en la sección 3 del archivo
6. solucionar_cflp
    [IO]6. Resolver el cflp para diferentes escenarios.
              a. Solución ingenua (todos los municipios tienen un centro de
                 distribución).
              b. Datos completos sin clusterizar.
              c. Dividido por clústers.
              La experimentación del caso especial de entrenamiento del modelo de pronóstico se
                puede encontrar en el historial de archivos en la sección 3 del archivo

## Estructura de directorios

El repositorio está estructurado de la siguiente manera:
La carpeta /data/ contiene los datos públicos de los municipios en los que se
tiene información.
La carpeta /funciones/ contiene los scripts de funciones que se utilizan en los
diferentes módulos.
La carpeta /resultados/ contiene los resultados de los diferentes módulos.
la carpeta /resultados-Extra/ contiene los resultados de los experimentos realizados de manera adicional.

El archivo main.ipybn contiene el código principal que se encarga de llamar a
los diferentes módulos y funciones.

para este se puede configurar distintos parametros y semillas aleatorias para la experimentación de los modelos.
