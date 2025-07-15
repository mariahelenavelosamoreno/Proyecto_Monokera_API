"""
ETL Pipeline para Blogs de Spaceflight News API

Descripción:
- Extrae datos de forma incremental desde la API (máx. 1,000 registros por ejecución).
- Transforma y valida la calidad de los datos (formato de fechas, duplicados, etc.).
- Almacena los datos en 2 capas:
  * RAW: Datos crudos (formato original de la API).
  * STAGING: Datos limpios y estandarizados (CSV con separador ';').

Flujo:
1. Extracción → 2. Validación RAW → 3. Transformación → 4. Validación STAGING

Uso:
- Ejecución diaria programada (schedule_interval='@daily').
- Puede iniciarse manualmente para backfills.
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import pandas as pd
import os
import json
from pandas import json_normalize
import great_expectations as gx
from great_expectations.core.expectation_suite import ExpectationSuite

# ==============================================
# CONFIGURACIÓN BASE
# ==============================================
DEFAULT_CONFIG = {
    "BASE_URL": "https://api.spaceflightnewsapi.net/v4/articles/",  # Endpoint oficial
    "LIMIT": 500,                   # Límite máximo por request (API)
    "STATE_FILE": "state/state_articles.json",  # Ruta para guardar estado de paginación
    "MAX_ARTICLES": 1000,           # Límite global por ejecución
    "RAW_DIR": "raw/",              # Directorio para datos crudos
    "STAGING_DIR": "staging/",      # Directorio para datos transformados
    "RAW_EXPECTATION_SUITE": "expectations/raw.json",       # Reglas para validar RAW
    "STAGING_EXPECTATION_SUITE": "expectations/staging.json" # Reglas para STAGING
}

# ==============================================
# FUNCIONES AUXILIARES
# ==============================================
def load_state(state_file):
    """Carga el último offset procesado desde un archivo JSON.
    
    Args:
        state_file (str): Ruta del archivo JSON (ej: 'state/state_articles.json').
    
    Returns:
        dict: {'offset': int}. Si no existe, devuelve {'offset': 0}.
    """
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            return json.load(f)
    return {"offset": 0}

def save_state(state_file, offset):
    """Guarda el offset actual en un archivo JSON para la próxima ejecución.
    
    Args:
        state_file (str): Ruta del archivo JSON.
        offset (int): Último offset procesado.
    """
    os.makedirs(os.path.dirname(state_file), exist_ok=True)
    with open(state_file, "w") as f:
        json.dump({"offset": offset}, f)

def fetch_articles(base_url, limit, offset):
    """Obtiene datos paginados de la API.
    
    Args:
        base_url (str): Endpoint de la API.
        limit (int): Máx. registros por request.
        offset (int): Punto de inicio para paginación.
    
    Returns:
        list: Datos en bruto (JSON parseado).
    
    Raises:
        HTTPError: Si la API devuelve status code != 200.
    """
    params = {
        "limit": limit,
        "offset": offset,
        "ordering": "updated_at"  # Ordenar para consistencia
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.json()["results"]

# ==============================================
# TAREAS PRINCIPALES (OPERADORES)
# ==============================================
def Start_ETL():
    """Inicializa el proceso ETL con marca de tiempo."""
    print(f"Iniciando ETL - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def End_ETL():
    """Finaliza el proceso ETL con marca de tiempo."""
    print(f"ETL completado - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def Extract_and_save_raw_csv(**kwargs):
    """
    Extrae datos de la API con paginación y guarda en CSV.
    
    Parámetros (Airflow Context):
        **kwargs: Recibe contexto de ejecución (ti, params, etc.).
    
    Retorna vía XComs:
        - 'raw_file': Ruta del CSV generado (ej: 'raw/2024-01-01_articles.csv').
        - 'raw_df': DataFrame en JSON (para pasar a la siguiente tarea).
    """
    ti = kwargs['ti']
    config = DEFAULT_CONFIG
    
    # 1. Cargar estado previo
    state = load_state(config["STATE_FILE"])
    current_offset = state["offset"]
    print(f"Iniciando extracción desde offset: {current_offset}")

    # 2. Extracción paginada
    data = []
    while len(data) < config["MAX_ARTICLES"]:
        try:
            articles = fetch_articles(config["BASE_URL"], config["LIMIT"], current_offset)
            if not articles:
                break  # Fin de los datos
            
            received = len(articles)
            data.extend(articles)
            current_offset += received
            print(f"Obtenidos {received} articles | Offset actual: {current_offset}")

            if len(data) >= config["MAX_ARTICLES"]:
                data = data[:config["MAX_ARTICLES"]]
                break
                
        except Exception as e:
            print(f"Error en extracción: {str(e)}")
            raise

    # 3. Guardado de datos brutos
    raw_df = json_normalize(data)
    os.makedirs(config["RAW_DIR"], exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_file = f"{config['RAW_DIR']}/{timestamp}_articles_raw.csv"
    
    try:
        raw_df.to_csv(output_file, sep=';', index=False)
        print(f"Datos RAW guardados en: {output_file}")
    except Exception as e:
        print(f"Error al guardar CSV: {str(e)}")
        raise

    # 4. Actualizar estado y compartir datos
    save_state(config["STATE_FILE"], current_offset)
    ti.xcom_push(key='raw_file', value=output_file)
    ti.xcom_push(key='raw_df', value=raw_df.to_json())

def Transform_and_save_staging_csv(**kwargs):
    """
    Transforma datos RAW a formato STAGING.
    
    Parámetros (Airflow Context):
        **kwargs: Recibe 'raw_df' desde XComs.
    
    Retorna vía XComs:
        - 'staging_file': Ruta del CSV transformado (ej: 'staging/2024-01-01_articles.csv').
    """
    ti = kwargs['ti']
    config = DEFAULT_CONFIG
    
    # 1. Cargar datos RAW
    raw_df_json = ti.xcom_pull(task_ids='Extract_and_save_raw_csv', key='raw_df')
    df = pd.read_json(raw_df_json)
    
    # 2. Transformaciones
    print("Aplicando transformaciones...")
    
    # Eliminar duplicados y ordenar
    df = df.drop_duplicates(subset=['id'])
    df = df.sort_values(by='updated_at')
    
    # Normalización de fechas
    df['published_datetime'] = pd.to_datetime(df['published_at'])
    df['published_at'] = df['published_datetime'].dt.strftime('%Y/%m/%d')
    df['updated_datetime'] = pd.to_datetime(df['updated_at'])
    df['updated_at'] = df['updated_datetime'].dt.strftime('%Y/%m/%d')
    
    # Limpieza de texto
    text_cols = ['title', 'authors', 'summary', 'news_site']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # 3. Guardado datos transformados
    os.makedirs(config["STAGING_DIR"], exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    staging_file = f"{config['STAGING_DIR']}/{timestamp}_articles_staging.csv"
    
    try:
        df.to_csv(staging_file, sep=';', index=False)
        print(f"Datos STAGING guardados en: {staging_file}")
    except Exception as e:
        print(f"Error al guardar STAGING: {str(e)}")
        raise
    
    ti.xcom_push(key='staging_file', value=staging_file)

def Validate_raw(**kwargs):
    """
    Valida datos RAW contra reglas de estructura.
    
    Validaciones (raw.json):
        - Campos obligatorios: 'id', 'title', 'published_at'.
        - 'id' único, fechas en formato ISO 8601.
    """
    ti = kwargs['ti']
    config = DEFAULT_CONFIG
    
    # 1. Cargar datos
    raw_file = ti.xcom_pull(task_ids='Extract_and_save_raw_csv', key='raw_file')
    if not raw_file:
        raise ValueError("No se encontró archivo RAW")
    
    try:
        df = pd.read_csv(raw_file, delimiter=";")
    except Exception as e:
        raise ValueError(f"Error leyendo RAW: {str(e)}")

    # 2. Cargar expectativas
    if not os.path.exists(config["RAW_EXPECTATION_SUITE"]):
        raise FileNotFoundError("Suite de validación RAW no encontrada")
    
    try:
        with open(config["RAW_EXPECTATION_SUITE"], 'r') as f:
            suite = ExpectationSuite(**json.load(f))
    except Exception as e:
        raise ValueError(f"Error cargando expectativas: {str(e)}")

    # 3. Ejecutar validación
    gx_df = gx.from_pandas(df)
    results = gx_df.validate(expectation_suite=suite)
    
    # 4. Analizar resultados
    errors = []
    for r in results['results']:
        if not r["success"]:
            errors.append(r["expectation_config"]["expectation_type"])
            print(f"❌ Validación fallida: {r['expectation_config']['expectation_type']}")

    if errors:
        raise ValueError(f"Errores en validación RAW: {', '.join(errors)}")
    
    print("✅ Validación RAW exitosa")

def Validate_staging(**kwargs):
    """
    Valida datos STAGING contra reglas de negocio.
    
    Validaciones (staging.json):
        - Formato 'YYYY/MM/DD' en fechas.
        - 'featured' es booleano.
    """
    ti = kwargs['ti']
    config = DEFAULT_CONFIG
    
    # 1. Cargar datos
    staging_file = ti.xcom_pull(task_ids='Transform_and_save_staging_csv', key='staging_file')
    if not staging_file:
        raise ValueError("No se encontró archivo STAGING")
    
    try:
        df = pd.read_csv(staging_file, delimiter=";")
    except Exception as e:
        raise ValueError(f"Error leyendo STAGING: {str(e)}")

    # 2. Cargar expectativas
    if not os.path.exists(config["STAGING_EXPECTATION_SUITE"]):
        raise FileNotFoundError("Suite de validación STAGING no encontrada")
    
    try:
        with open(config["STAGING_EXPECTATION_SUITE"], 'r') as f:
            suite = ExpectationSuite(**json.load(f))
    except Exception as e:
        raise ValueError(f"Error cargando expectativas: {str(e)}")

    # 3. Ejecutar validación
    gx_df = gx.from_pandas(df)
    results = gx_df.validate(expectation_suite=suite)
    
    # 4. Analizar resultados
    errors = []
    for r in results['results']:
        if not r["success"]:
            error_info = {
                "type": r["expectation_config"]["expectation_type"],
                "details": r.get("result", {})
            }
            errors.append(error_info)
            print(f"❌ Validación fallida: {error_info['type']}")

    if errors:
        error_msg = "\n".join([f"{i+1}. {e['type']} - {e['details']}" for i, e in enumerate(errors)])
        raise ValueError(f"Errores en validación STAGING:\n{error_msg}")
    
    print("✅ Validación STAGING exitosa")

# ==============================================
# DEFINICIÓN DEL DAG
# ==============================================
with DAG(
    dag_id='spaceflight_articles_etl',
    description='ETL para articles de Spaceflight News API',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['spaceflight', 'etl'],
) as dag:

    start_task = PythonOperator(
        task_id='Start_ETL',
        python_callable=Start_ETL
    )

    extract_task = PythonOperator(
        task_id='Extract_and_save_raw_csv',
        python_callable=Extract_and_save_raw_csv
    )

    transform_task = PythonOperator(
        task_id='Transform_and_save_staging_csv',
        python_callable=Transform_and_save_staging_csv
    )

    validate_raw_task = PythonOperator(
        task_id='Validate_raw',
        python_callable=Validate_raw
    )

    validate_staging_task = PythonOperator(
        task_id='Validate_staging',
        python_callable=Validate_staging
    )

    end_task = PythonOperator(
        task_id='End_ETL',
        python_callable=End_ETL
    )

    # Orquestación
    start_task >> extract_task
    extract_task >> [transform_task, validate_raw_task]
    transform_task >> validate_staging_task >> end_task