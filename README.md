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

[Ver Diagrama de Arquitectura en Lucidchart](https://lucid.app/lucidchart/988d7156-d739-4fa9-be01-a13a76fd7a4e/view)

### Flujo principal:

1. **Extracción:** Consumo de API → Datos RAW  
2. **Transformación:** Limpieza y formateo → Datos STAGING  
3. **Validación:** Verificación de calidad  
4. **Carga:** Generación de archivos finales

### Componentes:

- **Airflow** (Orquestación)  
- **Python** (Procesamiento)  
- **Great Expectations** (Validación)  
- **Docker** (Entorno de ejecución)

---

##  Configuración

### Requisitos previos

- Docker y Docker Compose  
- Python 3.10+  
- WSL2 (para usuarios Windows)

### Instalación

Clona el repositorio:



Inicia Airflow con Docker:

bash
Copiar
Editar
docker-compose up -d
Accede a la interfaz web:

URL: http://localhost:8080

Usuario: admin

Contraseña: admin (o consultar standalone_admin_password.txt)

📂 Estructura del Proyecto
perl
Copiar
Editar
spaceflight-etl/
├── dags/
│   ├── articles_etl.py           # Pipeline para artículos
│   └── blogs_etl.py              # Pipeline para blogs
├── expectations/                 # Definiciones de validación
│   ├── raw_articles.json
│   ├── staging_articles.json
│   ├── raw_blogs.json
│   └── staging_blogs.json
├── state/                        # Tracking de ejecuciones
│   └── state_articles.json
├── raw/                          # Datos brutos
├── staging/                      # Datos transformados
├── docs/                         # Documentación
├── docker-compose.yaml           # Configuración de Airflow
└── requirements.txt              # Dependencias Python
🚀 Ejecución
Los DAGs están programados para ejecutarse diariamente.
Para ejecutarlos manualmente:

Accede a la interfaz web de Airflow

Encuentra los DAGs spaceflight_articles_etl y spaceflight_blogs_etl

Actívalos y haz clic en "Trigger DAG"

🔍 Validaciones Implementadas
Se incluyen checks para:

Existencia de columnas obligatorias (id, title, etc.)

Formato correcto de fechas

Valores no nulos en campos críticos

Tipos de datos esperados

Unicidad de IDs

🧠 Retos Técnicos
Manejo de paginación: la API tiene límite de 500 registros por request, se implementó paginación con control de offset.

Estructura variable de datos: algunos campos opcionales requieren validación condicional.

Validación robusta: uso de Great Expectations en etapas RAW y STAGING.

Paralelización: validaciones se ejecutan en paralelo con transformaciones para eficiencia.

**Tiempos de Desarrollo**

| Etapa                              | Tiempo estimado |
|------------------------------------|-----------------|
| Diseño de arquitectura             | 2 horas         |
| Implementación ETL básico          | 4 horas         |
| Integración con Airflow            | 3 horas         |
| Validaciones y manejo de errores   | 5 horas         |
| Configuración del ambiente Docker  | 5 horas         |
| Documentación y ajustes finales    | 4 horas         |

###Mejoras Futuras
- Almacenamiento en la nube (S3 o GCS): Migrar los archivos locales a buckets en la nube para facilitar la escalabilidad y acceso distribuido.
- Monitoreo con alertas y métricas: Integrar herramientas como Prometheus + Grafana o Airflow + Slack para notificar fallos y medir rendimiento.
- Pruebas unitarias automáticas: Incorporar testing en los scripts de transformación y validación con pytest.
- CI/CD con GitHub Actions: Automatizar pruebas, validaciones y despliegues del pipeline.
- Backfilling: Implementar mecanismos para reprocesar históricos de forma controlada.
- Ingesta completa inicial en el primer DAG: Agregar una lógica alternativa para realizar una descarga completa de los datos históricos. Se propone usar un bucle con paginación automática para obtener todos los registros disponibles.
- Control incremental por updated_at: En lugar de fijar un límite estático de registros (como 1000), implementar un mecanismo que consulte la última fecha (updated_at) insertada por el DAG del día anterior y descargue solo los registros nuevos o actualizados:

### Recursos
- [Documentación oficial de Spaceflight News API](https://api.spaceflightnewsapi.net/v4/docs/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Great Expectations Documentation](https://docs.greatexpectations.io/docs/home/)
- [Docker Docs](https://docs.docker.com/)


