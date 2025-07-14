# Proyecto ETL para Spaceflight News API

##  Descripción del Proyecto

Este proyecto implementa un pipeline **ETL** para extraer datos de la API de **Spaceflight News** (artículos y blogs), transformarlos y cargarlos en archivos CSV. El sistema está construido con **Python** y **Apache Airflow**, permitiendo ejecuciones programadas y monitoreo del flujo de datos.

---

## Objetivos

- Extraer hasta **1000 registros** de los endpoints `/articles` y `/blogs`  
- Transformar los campos de fecha al formato `YYYY/MM/DD`  
- Generar archivos **CSV con separador `;`**  
- Implementar validaciones de calidad de datos  
- Crear un pipeline **automatizado y reproducible**

---

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

---

## Desarrollo Técnico del Pipeline ETL: Análisis, Construcción, Validación y Despliegue

## analisis preeliminar 
PONER PANTALLAZO DE RESULTADOS REELEVANTES
exploratorio, postmanm, notebooks, 
-nulos
-tipos de variable
-columnas.
-estructura de la data 

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
