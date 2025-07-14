<h1 align="center">Proyecto ETL para Spaceflight News API</h1>

#  Descripción del Proyecto

Este proyecto implementa un pipeline **ETL** para extraer datos de la API de **Spaceflight News** (artículos y blogs), transformarlos y cargarlos en archivos CSV. El sistema está construido con **Python** y **Apache Airflow**, permitiendo ejecuciones programadas y monitoreo del flujo de datos.

# Objetivos

- Extraer hasta **1000 registros** de los endpoints `/articles` y `/blogs`  
- Transformar los campos de fecha al formato `YYYY/MM/DD`  
- Generar archivos **CSV con separador `;`**  
- Implementar validaciones de calidad de datos  
- Crear un pipeline **automatizado y reproducible**

#  Arquitectura

<img width="1880" height="1055" alt="Diagrama de Arquitectura ETL API_ Spaceflight News (2)" src="https://github.com/user-attachments/assets/8c06c5ab-128b-44f4-af91-2e6650eac9de" />
<p align="center"><em><strong>Figura 1. Diagrama de arquitectura del pipeline ETL para la API de Spaceflight News.</strong></em></p>

### Flujo principal:

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

# Desarrollo Técnico del Pipeline ETL: Análisis, Construcción, Validación y Despliegue

### Analisis preeliminar

Para comprender la estructura y limitaciones de la fuente de datos, realicé una exploración inicial utilizando Postman, una herramienta que facilita la visualización, prueba y análisis de endpoints de APIs REST. A través de esta herramienta se evaluó el comportamiento del endpoint /articles y /blogs de la API pública de Spaceflight News:

- La documentación completa se encuentra disponible en:
https://api.spaceflightnewsapi.net/v4/docs

- Se identificó que la API tiene un límite de 500 registros por solicitud, configurable a través del parámetro _limit.

- A partir de este análisis, se diseñó una lógica de extracción basada en el uso de offset, de modo que se pueda obtener la totalidad de los datos disponibles en bloques de 500 sin duplicación.


<img width="1368" height="932" alt="image" src="https://github.com/user-attachments/assets/1eb3f20b-9333-4e2b-a4f6-df8189daa509" />
<p align="center"><em><strong>Figura 2. Ejemplo de respuesta de la API Spaceflight Blogs News analizada con Postman.</strong></em></p>


<img width="1363" height="935" alt="image" src="https://github.com/user-attachments/assets/85ebf1e0-19a1-4c62-8a44-8d8a40284acc" />
<p align="center"><em><strong>Figura 3. Ejemplo de respuesta de la API Spaceflight Articles News analizada con Postman.</strong></em></p>


### Control de duplicados y continuidad
Para evitar traer datos repetidos entre ejecuciones, se implementó un mecanismo de control de estado mediante archivos JSON (state/state_articles.json, state/state_blogs.json). Estos archivos almacenan el último offset procesado exitosamente, permitiendo que en cada nueva ejecución del pipeline, el proceso de extracción continúe desde el punto exacto en el que se detuvo anteriormente.

Adicionalmente, los datos se extraen en orden cronológico ascendente (de los más antiguos a los más recientes), asegurando un orden lógico en la construcción del histórico y facilitando futuras estrategias de ingesta incremental por fecha (updatedAt).

### Prevención de sobreescritura de archivos
Durante el proceso de carga en las capas RAW y STAGING, se implementó una convención de nombramiento de archivos basada en timestamp, utilizando el siguiente formato:

`datetime = pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M-%S')`.

Esta estrategia garantiza que:

- Cada archivo generado tenga un nombre único.

- No se sobrescriban archivos si el pipeline se ejecuta más de una vez en el mismo día.

- Se mantenga un histórico de ejecuciones, útil para auditoría, backfills o comparación entre versiones de datos.

### Exploración estructurada en notebooks
Todo el desarrollo inicial se realizó en Jupyter Notebooks, disponibles en el repositorio como:

`api_articles.ipynb`

`api_blogs.ipynb`

Estos notebooks sirvieron como entorno de prototipado para validar la conexión con la API, analizar la estructura de los datos, detectar inconsistencias y diseñar la lógica de extracción y transformación antes de integrarla a los DAGs de Airflow.

### Decisión de mantener las fuentes separadas
Aunque los endpoints de articles y blogs comparten una estructura de columnas prácticamente idéntica, se optó por manejar su procesamiento de forma separada desde el inicio. Esta decisión responde a las siguientes buenas prácticas en ingeniería de datos:

- Mantener independencia entre fuentes, facilitando trazabilidad y control por origen.

- Permitir la ejecución paralela o desacoplada de los pipelines.

- Adaptarse a futuras reglas de negocio o validaciones específicas para cada tipo de contenido.

## Diagnóstico del Dataset
Durante la exploración se realizaron las siguientes evaluaciones:

- Valores nulos: Se detectó que columnas críticas como id, title y publishedAt no deben contener valores nulos, mientras que campos como summary o listas como launches y events pueden estar vacíos sin afectar la integridad del dato.

- Tipos de variables: Se confirmó que los datos llegan como strings (para texto y fechas), enteros (para IDs) y listas (para relaciones). Se definieron transformaciones para convertir fechas al formato YYYY/MM/DD, validar consistencia en tipos y eliminar datos inconsistentes.

- Estructura de columnas: La estructura general incluye campos como id, title, summary, url, imageUrl, publishedAt, updatedAt, newsSite, launches, events, entre otros. Esta estructura es adecuada para construir una vista cronológica y temática del contenido informativo sobre misiones espaciales.

<p align="center"><img width="472" height="462" alt="image" src="https://github.com/user-attachments/assets/6252063e-eea2-4deb-b6d8-61cfe56b2e76" />
<p align="center"><em><strong>Figura 4. Estructura del DataFrame tras extracción de la API.</strong></em></p>


## Desarrollo de la lógica del pipeline DAG
El pipeline ETL fue desarrollado inicialmente en los notebooks api_articles.ipynb y api_blogs.ipynb, donde se validó paso a paso la lógica de extracción, transformación y validación de datos. Posteriormente, esta lógica fue migrada a un DAG de Apache Airflow, permitiendo una ejecución orquestada y programada del flujo completo.

- Para mantener la modularidad y trazabilidad del origen de datos, se diseñaron dos pipelines separados: uno para blogs y otro para artículos, a pesar de que ambos comparten la misma estructura de columnas. Esta separación permite:

- Trazabilidad por fuente

- Validaciones diferenciadas

- Escalabilidad y mantenibilidad del sistema

- Posible ejecución paralela

###DAG spaceflight_blogs_etl y spaceflight_articles_etl
Este DAG implementa un flujo ETL completo con cinco tareas principales:

- Start_ETL: Inicia el flujo y registra una marca temporal. Esto es útil para auditoría y control de ejecuciones.

- Extract_and_save_raw_csv: Realiza la extracción de datos desde el endpoint de blogs utilizando paginación (limit=500 y offset incremental). La lógica se apoya en un archivo state/state_blogs.json que guarda el último offset procesado, lo cual evita duplicados en ejecuciones futuras. Los datos extraídos se almacenan en formato CSV en la carpeta raw/, usando un timestamp en el nombre del archivo para prevenir sobreescrituras.
- Transform_and_save_staging_csv: aplica transformaciones esenciales como la eliminación de duplicados, la estandarización del formato de fechas en las columnas published_at y updated_at, y la limpieza de campos textuales para asegurar uniformidad. También convierte los tipos de datos según lo requerido. Finalmente, guarda el resultado en la carpeta staging/, utilizando un nombre de archivo con timestamp para evitar sobrescrituras y mantener trazabilidad entre ejecuciones.

- Validate_raw: Realiza validaciones de calidad sobre los datos en crudo (RAW) usando Great Expectations. Se verifica la presencia de columnas obligatorias, tipos de datos, unicidad de IDs y formato de fechas.

- Validate_staging Aplica una segunda capa de validación sobre los datos transformados (STAGING), asegurando que las reglas de negocio se cumplan antes de su uso analítico.

- End_ETL: Marca el fin del flujo e imprime el timestamp final de ejecución.

<img width="1123" height="262" alt="image" src="https://github.com/user-attachments/assets/bf7c34aa-5f22-45b4-8a35-293dd8d0a168" />
<p align="center"><em><strong>Figura 5. DAG de Airflow.</strong></em></p>

### Características clave del DAG

- Orquestación declarativa: Cada tarea está conectada mediante operadores >>, lo que permite un seguimiento visual del flujo.

- Reintentos y tolerancia a fallos: Airflow permite configurar reintentos automáticos para cada tarea en caso de error.

- XComs: Se utilizan para compartir resultados intermedios entre tareas, como el path del archivo CSV generado o el DataFrame en formato JSON.

- Validación robusta: Ambas capas (RAW y STAGING) son validadas de manera independiente usando suites definidas en archivos JSON (expectations/).

- Modularidad: Las funciones que realizan cada paso están separadas y documentadas, facilitando su reutilización y mantenimiento.

## Validaciones Implementadas
Para asegurar la calidad y confiabilidad de los datos a lo largo del pipeline ETL, se implementaron validaciones automáticas utilizando la librería Great Expectations. Las validaciones se ejecutan externamente tras la descarga de los archivos CSV para conservar los datos originales, incluso si presentan errores. Esto evita que el pipeline elimine o modifique información valiosa, facilitando trazabilidad, control y decisiones informadas por parte del cliente. Estas validaciones se aplican en dos etapas clave del proceso:

- RAW: datos directamente extraídos de la API, sin transformaciones.

- STAGING: datos ya transformados y listos para su consumo.

Cada conjunto de datos tiene su propia Expectation Suite definida en archivos JSON (raw.json y staging.json), y se ejecutan automáticamente dentro del DAG de Airflow.

### Validaciones en la capa RAW

- No nulos en id :Se usa expect_column_values_to_not_be_null en la columna id, con mostly = 1.0, para asegurar que ningún registro tenga id vacío.
Esto es crítico ya que el campo id es clave para la trazabilidad y posterior validación de duplicados.

- IDs únicos : Se usa expect_column_values_to_be_unique, validando que no haya duplicados en los identificadores dentro del archivo crudo.
Esto garantiza que cada registro extraído represente una entidad distinta en la fuente.

- Estas validaciones están marcadas con stop_pipeline_on_failure = true en los metadatos, lo que significa que si se incumplen, el DAG se detiene para evitar procesar datos inconsistentes.

### Validaciones en la capa STAGING

- No nulos en id: Se repite la validación para confirmar que el proceso de transformación no haya introducido valores vacíos.

- IDs únicos: Asegura que no se generaron duplicados durante el procesamiento.

- Formato de fecha (published_at y updated_at): Se valida que ambas columnas de fecha respeten el formato %Y/%m/%d usando expect_column_values_to_match_strftime_format. Estas fechas fueron transformadas desde el formato original durante la etapa de STAGING. En lugar de sobrescribir las columnas originales, se optó por crear columnas auxiliares (published_datetime, updated_datetime) para conservar los datos crudos y facilitar auditorías o trazabilidad.

- Valores esperados en featured: Se utiliza expect_column_values_to_be_in_set para asegurar que el campo booleano featured contenga solo los valores true o false, evitando errores de tipo o registros mal formateados.

### Uso de Great Expectations
- Permite definir reglas declarativas, reutilizables y explícitas.

- Facilita el análisis automático de errores y generación de reportes.

- Se integra fácilmente con Airflow y pandas, sin necesidad de herramientas externas.

## Retos Técnicos

- **Manejo de paginación:**  La API de Spaceflight News impone un límite de 500 registros por solicitud. Para poder extraer más datos sin omitir información, se implementó una lógica de paginación controlada mediante `offset`, acumulando los resultados de forma iterativa hasta alcanzar el número deseado o agotar la fuente.

- **Validación robusta con Great Expectations:**  Se definieron dos etapas de validación: una al finalizar la extracción (RAW) y otra después de la transformación (STAGING). Esto permite detectar errores tanto en el origen como en la lógica de procesamiento, mejorando la calidad y confiabilidad de los datos entregados.

- **Despliegue del entorno con Docker:**  Se optó por usar **Docker** para garantizar la portabilidad del entorno y evitar los problemas comunes al instalar **Apache Airflow directamente en Windows**, como conflictos con dependencias, virtualenvs o errores en la inicialización del scheduler. Docker permitió encapsular toda la configuración del proyecto (Airflow, dependencias, rutas y volúmenes) en contenedores reproducibles, facilitando la ejecución en cualquier sistema operativo y asegurando coherencia entre entornos de desarrollo y producción.

## 🔧 Configuración del Entorno con Docker

Para asegurar portabilidad, aislamiento de dependencias y facilitar la ejecución del pipeline en cualquier entorno, se utilizó **Docker** como contenedor principal para la arquitectura de Airflow.

Se creó una configuración personalizada con los siguientes componentes:

### 📄 `Dockerfile`

Este archivo define la imagen base del entorno de ejecución, e incluye:

- Instalación de **dependencias específicas** como `pandas`, `requests`, `great_expectations`, y otras necesarias para el funcionamiento del pipeline.
- Configuración del entorno de trabajo y copia de los scripts ETL.

### docker-compose.yml
Este archivo orquesta los servicios necesarios para ejecutar Apache Airflow en contenedores aislados. Se incluyen:

airflow-webserver

airflow-scheduler

airflow-worker

postgres como backend

redis para el broker de mensajes

airflow-init para inicializar el entorno

- Algunos parámetros clave:

Montaje de volúmenes locales (./dags, ./logs, ./plugins)

Exposición de puertos (por ejemplo, 8080 para la interfaz web de Airflow)

Persistencia de datos en volúmenes de Docker


##  Mejoras Futuras

- **Almacenamiento en la nube (S3 o Data Warehouse):**   Migrar los archivos CSV almacenados localmente a buckets en la nube como Amazon S3, Google Cloud Storage o un Data Warehouse. Esto facilitará el acceso distribuido, el versionamiento, la escalabilidad y la integración con sistemas analíticos o BI.

- **Monitoreo y alertas automáticas:**  Integrar herramientas de monitoreo (como Slack o correo electrónico) para notificar fallos, validaciones fallidas o tareas omitidas. Esto mejoraría la visibilidad operativa y permitiría una respuesta más rápida ante errores.

- **Backfilling controlado:**  Incorporar lógica de backfilling que permita reprocesar datos históricos sin interferir con los flujos diarios. Esto sería útil para nuevos modelos, corrección de errores o auditorías.

- **Ingesta completa inicial (historical load):**  Diseñar un DAG alternativo capaz de extraer todo el histórico de datos disponibles mediante paginación completa. Esta lógica podría implementarse como un flujo one-time, aprovechando un bucle con `offset` hasta agotar los registros.
# Código para Extracción Histórica Completa (ETL)

`def Extract_full_historical_load(**kwargs):
    ti = kwargs['ti']
    config = DEFAULT_CONFIG
    
    print("Iniciando extracción HISTÓRICA completa (one-time)")

    # 1. Cargar estado previo (si existe)
    state_file = config["STATE_FILE"]
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
            last_offset = state.get("last_offset", 0)
            print(f"Offset inicial desde state.json: {last_offset}")
    except (FileNotFoundError, json.JSONDecodeError):
        last_offset = 0
        print("No se encontró state.json. Iniciando desde offset 0")

    # 2. Configuración de la extracción
    current_offset = last_offset  # Comienza desde el último offset conocido
    data = []
    extraction_active = True
    max_records = float('inf')  # Sin límite de registros

    # 3. Extracción paginada completa
    while extraction_active and len(data) < max_records:
        try:
            blogs = fetch_blogs(config["BASE_URL"], config["LIMIT"], current_offset)
            
            if not blogs:  # Fin de los datos
                print(" No hay más registros en la API")
                extraction_active = False
                break
                
            # Agregar datos y actualizar offset
            received = len(blogs)
            data.extend(blogs)
            current_offset += received
            
            # Actualizar estado en cada iteración (para resiliencia)
            with open(state_file, 'w') as f:
                json.dump({"last_offset": current_offset}, f)
            
            print(f" Lote recibido: {received} registros | Offset acumulado: {current_offset}")

            # Pequeño delay para evitar rate-limiting
            time.sleep(0.3)  
            
        except Exception as e:
            print(f" Error en extracción histórica: {str(e)}")
            # Conserva el último offset válido
            with open(state_file, 'w') as f:
                json.dump({"last_offset": current_offset}, f)
            raise

    # 4. Guardado de datos brutos
    if data:
        raw_df = pd.json_normalize(data)
        os.makedirs(config["RAW_DIR"], exist_ok=True)
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        output_file = f"{config['RAW_DIR']}/FULL_HISTORICAL_{timestamp}_blogs_raw.csv"
        
        try:
            raw_df.to_csv(output_file, sep=';', index=False)
            print(f"Extracción histórica completada. Total registros: {len(data)}")
            print(f"Archivo generado: {output_file}")

            # Actualizar estado final
            with open(state_file, 'w') as f:
                json.dump({"last_offset": current_offset, "last_execution": timestamp}, f)

            # Compartir metadatos
            ti.xcom_push(key='historical_raw_file', value=output_file)
            ti.xcom_push(key='total_records', value=len(data))
            
        except Exception as e:
            print(f"Error al guardar CSV histórico: {str(e)}")
            raise
    else:
        print("No se encontraron registros nuevos en la API")

    # 5. Log del estado final
    print("\n--- ESTADO FINAL ---")
    print(f"Último offset procesado: {current_offset}")
    print(f"Registros totales extraídos: {len(data)}")`

- **Control incremental con `updated_at`:**  Implementar una lógica de ingesta que no dependa de un límite fijo de registros, sino que utilice la columna `updated_at` para consultar solo los datos nuevos o actualizados desde la última ejecución exitosa. Esto permitiría mantener el dataset actualizado en tiempo real.

- **Gestión de ejecuciones sin nuevos datos:**  Añadir una condición al DAG para que, si no se detectan nuevos registros por extraer, simplemente se salte la ejecución sin lanzar errores, y registre un log que indique "sin cambios".
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
