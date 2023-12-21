# Manejo de Datos



> **Nota:** Esta sección está en construcción.

Los datos utilizados para la generación del testeo de la librería se encuentran en la carpeta `aior/test/data/`. Adicionalmente, los datos provienen de las API's de [Datos Abiertos Colombia](https://www.datos.gov.co/), los microdatos del [DANE](https://microdatos.dane.gov.co/index.php/catalog/central/about), [Unidad de Planificación Rural Agropecuaria - UPRA Colombia](https://upra.gov.co/en), [Open Street Map](https://nominatim.openstreetmap.org/ui/search.html), [Google Maps](https://www.google.com/maps/), [OSRM](http://project-osrm.org/), [GeoPandas](https://geopandas.org/), [GeoPy](https://geopy.readthedocs.io/en/stable), [GeoNames](https://www.geonames.org/) y finalmente, información de  [Wikipedia](https://www.wikipedia.org/) y [2016 European Guidelines on cardiovascular disease prevention in clinical practice](https://doi.org/10.1093/eurheartj/ehw106).


La aplicación del flujo de trabajo propuesto se realizará para la resolución de un problema de localización de instalaciones con restricciones de capacidad en el caso de la logística alimenticia en Colombia.

Se busca entonces encontrar una solución a la siguiente pregunta:

¿Dónde ubicar las instalaciones de distribución de alimentos para minimizar los costos de transporte y cumplir con la demanda de los clientes (población colombiana)?

Para esto se encontró la siguiente información disponible en las bases de datos anteriormente mencionadas, que son de orden público y se encuentran disponibles en la web:

- Centros de distribución
    > Información con respecto a la capacidad de las instalaciones, es decir, la cantidad de alimentos que pueden almacenar las instalaciones y sus costos de instalacción.
    
    <!-- TODO: #12 Decir de donde estimo las capacidades que pueden tener los lugares -->
    > Las capacidades de las instalaciones aun no están calculadas
    - Municipios de Colombia [Datos Abiertos Colombia](https://www.datos.gov.co/resource/gdxc-w37w.json).

- Orígenes
    > Información con respecto a de donde provienen los alimentos, es decir, los municipios de Colombia que producen alimentos y la cantidad de alimentos que producen.
    - Municipios de Colombia [Datos Abiertos Colombia](https://www.datos.gov.co/resource/gdxc-w37w.json).
    - Municipios y la cantidad de alimentos que producen [UPRA](https://upra.gov.co/es-co/Paginas/eva_2022.aspx).
    - Ubicación de los municipios de Colombia que producen alimentos [Open Street Map](https://nominatim.openstreetmap.org/ui/search.html), [Google Maps](https://www.google.com/maps/), [Wikipedia](https://www.wikipedia.org/), [OSRM](http://project-osrm.org/), [GeoPandas](https://geopandas.org/), [GeoPy](https://geopy.readthedocs.io/en/stable), [GeoNames](https://www.geonames.org/).
    - Abastecimiento de alimentos por municipio de Colombia que produce alimentos [SIPSA, DANE](https://www.dane.gov.co/index.php/estadisticas-por-tema/agropecuario/sistema-de-informacion-de-precios-sipsa/componente-abastecimientos-1).

- Destinos-Demanda
    > Información con respecto a donde se encuentran los clientes, es decir, los municipios de Colombia que demandan alimentos y la cantidad de alimentos que demandan.
    
    No se encontró información literal con respecto a la demanda de alimentos en colombia, pero se encontró información con respecto a la población colombiana, por lo tanto se asume que la demanda de alimentos es proporcional a la población colombiana por municipio.

    - Poblacion colombiana por municipio [DANE](https://www.dane.gov.co/index.php/estadisticas-por-tema/demografia-y-poblacion/proyecciones-de-poblacion).
    - Consumo de alimentos por persona [2016 European Guidelines on cardiovascular disease prevention in clinical practice](https://academic.oup.com/eurheartj/article/37/29/2315/1748952).

- Costos de transporte
    > Información con respecto a los costos de transporte entre los municipios de Colombia. Es decir, la distancia entre los municipios de Colombia y el costo de transporte entre ellos.

    - Distancia entre los municipios de Colombia. [OSRM](http://project-osrm.org/), [Google Maps](https://www.google.com/maps/), [GeoPandas](https://geopandas.org/).
    - Costo de transporte entre los municipios de Colombia.  [Ministerio de Transporte](https://www.mintransporte.gov.co/publicaciones/4462/sice-tac/).

---
>[!NOTE]
>Los elementos marcados en <a style='color:red'>rojo</a> son los que se consideran claves para la construcción de una red de distribución.<br>
Con <a style='color:blue'>azul</a> se marcan los elementos que se utilizarán para enlazar las bases de datos, haciendo más comodo tener un id único para cada municipio preestablecido por el DANE.

## Centros de Distribución

Se considera que cualquier área poblada registrada por el DANE puede ser un centro de distribución, por lo tanto, se considera que los municipios de Colombia son los posibles puntos claves a determinar, para esto es importante tenerlos indexados, identificados y con sus coordenadas geográficas.

### Municipios de Colombia

En Colombia se reconocen actualmente 1123 municipios ([Datos Abiertos Colombia](https://www.datos.gov.co/Mapas-Nacionales/Departamentos-y-municipios-de-Colombia/xdk5-pm3f/about_data)), [Aquí](https://www.datos.gov.co/resource/gdxc-w37w.json) y [Aquí](https://www.datos.gov.co/resource/xdk5-pm3f.json) se encuentran los enlaces a las API's con la información de los municipios de Colombia. para todos estos se requiere conocer los datos de región, departamento, municipio, latitud y longitud. Es decir, una base de datos con la siguiente forma:

| <a style='color:red'>id</a> | Región | Departamento | Municipio | <a style='color:blue'>Latitud</a> | <a style='color:blue'>Longitud</a> |
|:---:|:---:|:---:|:---:|:---:|:---:|
| ##### | "#####" | "#####" | "#####" | ##### | ##### |

Para obtener esta estructura se utiliza la API de [Datos Abiertos Colombia](https://www.datos.gov.co/Mapas-Nacionales/Departamentos-y-municipios-de-Colombia/xdk5-pm3f/about_data), que contiene la información de los municipios de Colombia, para extraerlos, se usa la librería `requests` `sodapy` y `pandas` de python.

>[!NOTE]
>En los datos se encuentra que existe perdida en la información de `id=c_digo_dane_del_departamento`, por la existencia de 0 a izquierda y derecha, que se corrige añadiendo a izquierda y posteriormente a derecha uno o dos ceros hasta que se tenga el código completo de 5 dígitos. (se realizó una comprobación de esto con una muestra de 100 departamentos y municipios, y se encontró que todos los códigos de departamento y municipio se encuentran completos).

Con estos nombres, se extrae la latitud y longitud de cada municipio utilizando la API de [Open Street Map](https://nominatim.openstreetmap.org/ui/search.html). Usando como parametro de busqueda la cadena de texto '*string*' `municipio, departamento, pais`.

Casos especiales: (que por errores de escritura en la base de datos no se encuentran en la API de Open Street Map)

- Dibula, La Guajira, Colombia -> Dibulla, La Guajira, Colombia
- Tolú Viejo, Sucre, Colombia -> Tolúviejo, Sucre, Colombia
- San Juan de Río Seco, Cundinamarca, Colombia -> San Juan de Ríoseco, Cundinamarca, Colombia
- San Luis de Gaceno, Casanare, Colombia -> San Luis de Gaceno, <a style='color:red'> Boyacá </a>, Colombia
> **Nota:** Se Obta por San Luis de Gaceno, Boyacá, Colombia, dado que San Luis de Gaceno, Casanare, Colombia no se encuentra, y San Luis de Gaceno, Boyacá, Colombia es el municipio más cercano.
<!-- *TODO #2 check if the information is right -->
- Villa de San Diego de Ubate, Cundinamarca, Colombia -> Ubaté, Provincia de Ubaté, Colombia
- El Cantón del San Pablo, Chocó, Colombia -> El Cantón de San Pablo, Chocó, Colombia
- Valle de Guamez, Putumayo, Colombia -> Valle Del Guamuez, Putumayo, Colombia
- San Pablo de Borbur, Bolívar, Colombia -> San Pablo de Borbur, Boyaca, Colombia o San Pablo, Bolívar, Colombia
> **Nota:** Se Obta por San Pablo, Bolívar, Colombia, dado que San Pablo de Borbur, Boyaca, Colombia ya se encuentra en la base de datos.
- San Andrés de Tumaco, Nariño, Colombia -> Tumaco, Nariño, Colombia.

### Costos de Instalación

Para la construcción de una instalación se requiere de un costo de instalación, que se asume que es proporcional a la capacidad de la instalación. Es decir, a mayor capacidad de la instalación, mayor costo de instalación.

<!-- TODO: #13 Añadir los costos de Instalación -->

### Capacidades de las Instalaciones

Para la construcción de una instalación se requiere de una capacidad de almacenamiento, que se asume que es proporcional a la capacidad de la instalación. Es decir, a mayor capacidad de la instalación, mayor costo de instalación.

## Orígenes

Se considera que cualquier área poblada que registre en los datos del UPRA puede ser un origen, por lo tanto, se considera que los municipios de Colombia que producen alimentos son los posibles puntos claves a determinar, para esto es importante tenerlos indexados, identificados y con sus coordenadas geográficas, además, existe una capacidad infinita de ingreso de alimentos por parte de los puertos, los cuales se consideran como puntos de origen.

### Municipios de Colombia que producen alimentos

Los datos de origenes de alimentos en colombia se encuentran en la página de la [UPRA](https://upra.gov.co/es-co/Paginas/eva_2022.aspx) desde 2019 hasta 2022, en la cual se encuentran los datos de los municipios de Colombia que producen alimentos con información de toneladas producidas y área cultivada, ocurren los mismos problemas de indice que en los datos de los municipios de Colombia, por lo tanto, se utiliza la misma solución.

Los grupos de cultivos encontrados son:


### Municipios y la cantidad de alimentos que producen

### Ubicación de los municipios de Colombia que producen alimentos

### Abastecimiento de alimentos por municipio de Colombia que produce alimentos

## Destinos-Demanda

### Poblacion colombiana por municipio

### Consumo de alimentos por persona

## Costos de transporte

### Distancia entre los municipios de Colombia

### Costo de transporte entre los municipios de Colombia