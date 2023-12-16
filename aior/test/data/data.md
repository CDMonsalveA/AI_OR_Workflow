# Manejo de Datos

> **Nota:** Esta sección está en construcción.

Los datos utilizados para la generación del testeo de la librería se encuentran en la carpeta `aior/test/data/`. Adicionalmente, los datos provienen de las API's de [Datos Abiertos Colombia](https://www.datos.gov.co/), [DANE](https://microdatos.dane.gov.co/index.php/catalog/central/about), [Unidad de Planificación Rural Agropecuaria - UPRA Colombia](https://upra.gov.co/en)

<!-- *TODO #1 check if all the sources are here -->

La aplicación del flujo de trabajo propuesto se realizará para la resolución de un problema de localización de instalaciones con restricciones de capacidad en el caso de la logística alimenticia en Colombia.

Se busca entonces encontrar una solución a la siguiente pregunta:

¿Dónde ubicar las instalaciones de distribución de alimentos para minimizar los costos de transporte y cumplir con la demanda de los clientes (población colombiana)?

Para esto se requiere identificar:

- Orígenes
- Destinos
- Demanda de clientes
- Capacidades
- Costos de transporte
- Costos de apertura de instalaciones

## Datos de Orígenes y Destinos

Los datos de Orígenes y Destinos se refiere a todos los municipios de Colombia (región, departamento, municipio, latitud, longitud, habitantes, demanda de alimentos, etc.).

Lamentablemente, no existe una base de datos en colombia que contenga esta información en alguno de los medios oficiales, por lo tanto se optó por construirla a partir de la información de los municipios de Colombia que se encuentra en la API de [Datos Abiertos Colombia](https://www.datos.gov.co/).

[Aquí](https://www.datos.gov.co/resource/gdxc-w37w.json) y [Aquí](https://www.datos.gov.co/resource/xdk5-pm3f.json) se encuentran los enlaces a las API's con la información de los municipios de Colombia.

De aquí se obtiene la siguiente información:
- Nombre del País (pais)
- <a style='color:red'>Nombre del Departamento (departamento)</a>
- Codigo del Departamento
- <a style='color:red'>Nombre del Municipio (municipio)</a>
- Codigo del Municipio
que se encuentra en el archivo `aior/test/data/municipios.json & municipios.cvs`.

Los elementos marcados en <a style='color:red'>rojo</a> son los que se utilizarán para la construcción de la base de datos de Orígenes y Destinos.

Con estos nombres, se extrae la latitud y longitud de cada municipio utilizando la API de [Open Street Map](https://nominatim.openstreetmap.org/ui/search.html). Usando como parametro de busqueda la cadena de texto '*string*' `municipio, departamento, pais`.





