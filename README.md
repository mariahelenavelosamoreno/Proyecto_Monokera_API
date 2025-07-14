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

```bash
git clone https://github.com/tu-usuario/spaceflight-etl.git
cd spaceflight-etl

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

⏱️ Tiempos de Desarrollo
Etapa	Tiempo estimado
Diseño de arquitectura	2 horas
Implementación ETL básico	4 horas
Integración con Airflow	3 horas
Validaciones y manejo de errores	5 horas
Documentación y ajustes finales	2 horas

📈 Mejoras Futuras
💾 Almacenamiento en la nube (S3 o GCS)

📊 Monitoreo con alertas y métricas

🧪 Pruebas unitarias automáticas

🔁 CI/CD con GitHub Actions

📆 Backfilling para reprocesar históricos

📚 Recursos
Documentación oficial de Spaceflight News API

Apache Airflow Documentation

Great Expectations Documentation

yaml
Copiar
Editar

