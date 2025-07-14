# Proyecto ETL para Spaceflight News API

##  Descripción del Proyecto

Este proyecto implementa un pipeline **ETL** para extraer datos de la API de **Spaceflight News** (artículos y blogs), transformarlos y cargarlos en archivos CSV. El sistema está construido con **Python** y **Apache Airflow**, permitiendo ejecuciones programadas y monitoreo del flujo de datos.

## Objetivos

- Extraer hasta **1000 registros** de los endpoints `/articles` y `/blogs`  
- Transformar los campos de fecha al formato `YYYY/MM/DD`  
- Generar archivos **CSV con separador `;`**  
- Implementar validaciones de calidad de datos  
- Crear un pipeline **automatizado y reproducible**

##  Arquitectura

<img width="1880" height="1055" alt="Diagrama de Arquitectura ETL API_ Spaceflight News (2)" src="https://github.com/user-attachments/assets/8c06c5ab-128b-44f4-af91-2e6650eac9de" />

## Flujo principal:

1. **Extracción:** Consumo de API → Datos RAW  
2. **Transformación:** Limpieza y formateo → Datos STAGING  
3. **Validación:** Verificación de calidad  
4. **Carga:** Generación de archivos finales

### Modelo de Arquitectura por Capas (Medallion Architecture)

El flujo principal del pipeline sigue una estructura basada en la arquitectura Medallion, que organiza el tratamiento de los datos en capas sucesivas para mejorar su calidad, trazabilidad y gobernanza.

Actualmente, se implementan las siguientes capas:

- Capa RAW (Bronze): Corresponde a la extracción directa de datos desde la API de Spaceflight News. Esta capa almacena los datos en su forma más cruda, sin transformaciones ni filtrado, y sirve como respaldo fiel del origen para trazabilidad y reprocesos. En este proyecto, esta capa se encuentra representada por la carpeta /raw.

- Capa STAGING (Silver): Representa los datos ya transformados y limpios. En esta etapa se realiza el formateo de fechas, normalización de tipos, eliminación de nulos críticos y otras transformaciones ligeras. El objetivo es dejar los datos listos para análisis o pasos posteriores. Se materializa en la carpeta /staging.

- Capa GOLD (no implementada aún): Esta capa normalmente contiene datos enriquecidos, consolidados o listos para ser consumidos por el negocio o herramientas de BI.
En este caso, aún no se ha implementado debido a que no se cuenta con requerimientos específicos del negocio sobre cómo deben ser los datos finales ni qué métricas o indicadores se desean construir. La construcción de esta capa dependerá directamente del conocimiento del dominio y de los objetivos analíticos definidos por los stakeholders. Esto puede incluir agregaciones, joins con otras fuentes o cálculos complejos específicos para reportes.

### Componentes:

- **Airflow** (Orquestación)  
- **Python** (Procesamiento)  
- **Great Expectations** (Validación)  
- **Docker** (Entorno de ejecución)

## Desarrollo Técnico del Pipeline ETL: Análisis, Construcción, Validación y Despliegue

## Analisis preeliminar

Para comprender la estructura y limitaciones de la fuente de datos, realicé una exploración inicial utilizando Postman, una herramienta que facilita la visualización, prueba y análisis de endpoints de APIs REST. A través de esta herramienta se evaluó el comportamiento del endpoint /articles y /blogs de la API pública de Spaceflight News:

- La documentación completa se encuentra disponible en:
https://api.spaceflightnewsapi.net/v4/docs

- Se identificó que la API tiene un límite de 500 registros por solicitud, configurable a través del parámetro _limit.

- A partir de este análisis, se diseñó una lógica de extracción basada en el uso de offset, de modo que se pueda obtener la totalidad de los datos disponibles en bloques de 500 sin duplicación.

***Blogs***
<img width="1368" height="932" alt="image" src="https://github.com/user-attachments/assets/1eb3f20b-9333-4e2b-a4f6-df8189daa509" />

***Articles***
<img width="1363" height="935" alt="image" src="https://github.com/user-attachments/assets/85ebf1e0-19a1-4c62-8a44-8d8a40284acc" />

## Control de duplicados y continuidad
Para evitar traer datos repetidos entre ejecuciones, se implementó un mecanismo de control de estado mediante archivos JSON (state/state_articles.json, state/state_blogs.json). Estos archivos almacenan el último offset procesado exitosamente, permitiendo que en cada nueva ejecución del pipeline, el proceso de extracción continúe desde el punto exacto en el que se detuvo anteriormente.

Adicionalmente, los datos se extraen en orden cronológico ascendente (de los más antiguos a los más recientes), asegurando un orden lógico en la construcción del histórico y facilitando futuras estrategias de ingesta incremental por fecha (updatedAt).

## Prevención de sobreescritura de archivos
Durante el proceso de carga en las capas RAW y STAGING, se implementó una convención de nombramiento de archivos basada en timestamp, utilizando el siguiente formato:

`datetime = pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M-%S')`.

Esta estrategia garantiza que:

- Cada archivo generado tenga un nombre único.

- No se sobrescriban archivos si el pipeline se ejecuta más de una vez en el mismo día.

- Se mantenga un histórico de ejecuciones, útil para auditoría, backfills o comparación entre versiones de datos.

## Exploración estructurada en notebooks
Todo el desarrollo inicial se realizó en Jupyter Notebooks, disponibles en el repositorio como:

`api_articles.ipynb`

`api_blogs.ipynb`

Estos notebooks sirvieron como entorno de prototipado para validar la conexión con la API, analizar la estructura de los datos, detectar inconsistencias y diseñar la lógica de extracción y transformación antes de integrarla a los DAGs de Airflow.

## Decisión de mantener las fuentes separadas
Aunque los endpoints de articles y blogs comparten una estructura de columnas prácticamente idéntica, se optó por manejar su procesamiento de forma separada desde el inicio. Esta decisión responde a las siguientes buenas prácticas en ingeniería de datos:

- Mantener independencia entre fuentes, facilitando trazabilidad y control por origen.

- Permitir la ejecución paralela o desacoplada de los pipelines.

- Adaptarse a futuras reglas de negocio o validaciones específicas para cada tipo de contenido.

## Diagnóstico del Dataset
Durante la exploración se realizaron las siguientes evaluaciones:

- Valores nulos: Se detectó que columnas críticas como id, title y publishedAt no deben contener valores nulos, mientras que campos como summary o listas como launches y events pueden estar vacíos sin afectar la integridad del dato.

- Tipos de variables: Se confirmó que los datos llegan como strings (para texto y fechas), enteros (para IDs) y listas (para relaciones). Se definieron transformaciones para convertir fechas al formato YYYY/MM/DD, validar consistencia en tipos y eliminar datos inconsistentes.

- Estructura de columnas: La estructura general incluye campos como id, title, summary, url, imageUrl, publishedAt, updatedAt, newsSite, launches, events, entre otros. Esta estructura es adecuada para construir una vista cronológica y temática del contenido informativo sobre misiones espaciales.

<img width="472" height="462" alt="image" src="https://github.com/user-attachments/assets/6252063e-eea2-4deb-b6d8-61cfe56b2e76" />

---

### desarrollo de la logica del pipeline DAG
primero se realizo en notebooks (nombrar el nombre de los archivos) explicar mas o menos que
explicar realmente como funciona el codigo y como funciona el script y decir que estas estan orquestadas por el dag 
PANTALLAZO DEL DAG

### Validaciones Implementadas
Se incluyen checks para:

Existencia de columnas obligatorias (id, title, etc.)
ser mas especifica con lo que realmente estoy haciendo en cada uno de los pasos de la validacion explicando el porque codigo 

Formato correcto de fechas que fechas estoy cambiando, cuales y cuales agregue y porque agregar y no reemplarzar completamebnte

Valores no nulos en campos críticos, dar argumentos

Tipos de datos esperados ser mas especificas en eso 

Unicidad de IDs

### Retos Técnicos
Manejo de paginación: la API tiene límite de 500 registros por request, se implementó paginación con control de offset.

Validación robusta: uso de Great Expectations en etapas RAW y STAGING. una vez llega la data se validfa y una vez llega se valida nuevamebnte

despliegue del servidor en docker


### Mejoras Futuras
- Almacenamiento en la nube (S3 o DW): Migrar los archivos locales a buckets en la nube para facilitar la escalabilidad y acceso distribuido.
- Monitoreo con alertas Slack para notificar fallos y medir rendimiento.
- Backfilling: Implementar mecanismos para reprocesar históricos de forma controlada. Ingesta completa inicial en el primer DAG: Agregar una lógica alternativa para realizar una descarga completa de los datos históricos. Se propone usar un bucle con paginación automática para obtener todos los registros disponibles.
- Control incremental por updated_at: En lugar de fijar un límite estático de registros (como 1000), implementar un mecanismo que consulte la última fecha (updated_at) insertada por el DAG del día anterior y descargue solo los registros nuevos o actualizados:
- CUANDO NO HAYA DATA QUE SOLO skip y no lance error que avise que no hay mas data oara extraer

---

### Tiempos de Desarrollo

| Etapa                              | Tiempo estimado |
|------------------------------------|-----------------|
| Diseño de arquitectura             | 2 horas         |
| Implementación ETL básico          | 4 horas         |
| Integración con Airflow            | 3 horas         |
| Validaciones y manejo de errores   | 5 horas         |
| Configuración del ambiente Docker  | 5 horas         |
| Documentación y ajustes finales    | 4 horas         |


### Recursos
- [Documentación oficial de Spaceflight News API](https://api.spaceflightnewsapi.net/v4/docs/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Great Expectations Documentation](https://docs.greatexpectations.io/docs/home/)
- [Docker Docs](https://docs.docker.com/)
