# 🛰️ Proyecto ETL para Spaceflight News API

## 📌 Descripción del Proyecto

Este proyecto implementa un pipeline **ETL** para extraer datos de la API de **Spaceflight News** (artículos y blogs), transformarlos y cargarlos en archivos CSV. El sistema está construido con **Python** y **Apache Airflow**, permitiendo ejecuciones programadas y monitoreo del flujo de datos.

---

## 🎯 Objetivos

- Extraer hasta **1000 registros** de los endpoints `/articles` y `/blogs`  
- Transformar los campos de fecha al formato `YYYY/MM/DD`  
- Generar archivos **CSV con separador `;`**  
- Implementar validaciones de calidad de datos  
- Crear un pipeline **automatizado y reproducible**

---

## 🏗️ Arquitectura

![Arquitectura del Proyecto](https://lucid.app/lucidchart/988d7156-d739-4fa9-be01-a13a76fd7a4e/view)

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

## 🛠️ Configuración

### Requisitos previos

- Docker y Docker Compose  
- Python 3.10+  
- WSL2 (para usuarios Windows)

### Instalación

Clona el repositorio:

```bash
git clone https://github.com/tu-usuario/spaceflight-etl.git
cd spaceflight-etl
