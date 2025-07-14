# Apache Airflow con Docker

![Airflow Logo](https://airflow.apache.org/images/feature-image.png)

## 🐳 Inicialización de Airflow con Docker

### Requisitos para Windows
Si estás en Windows, necesitarás:
1. Docker Desktop instalado
2. WSL (Windows Subsystem for Linux) activado

🔗 [Descargar Docker Desktop](https://www.docker.com/products/docker-desktop)

### Configuración inicial
1. Obtén el archivo `docker-compose.yml` oficial de Airflow:
   ```bash
   curl -LfO 'https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml'
   ```
   (Para desarrollo, puedes extraer solo el primer contenedor)

2. Configura las variables de entorno:
   ```bash
   export AIRFLOW_PROJ_DIR=$(pwd)
   ```

### 🚀 Despliegue
Ejecuta el siguiente comando para iniciar los contenedores:
```bash
docker-compose up
```

### 🔑 Acceso al servidor
- El servidor estará disponible en: [http://localhost:8080](http://localhost:8080)
- Credenciales:
  - Usuario: `admin`
  - Contraseña: Consulta el archivo `standalone_admin_password.txt`

---

## 🐍 Configuración adicional para entorno local (Python Notebooks)

### Requisitos
- Python 3.10 instalado
- Se recomienda usar un entorno virtual

### 🛠 Configuración del entorno virtual

**Windows:**
```powershell
# Primero habilita la ejecución de scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Crea y activa el entorno
python -m venv venv
.\venv\Scripts\activate
```

**Mac/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 📦 Instalación de dependencias
```bash
pip install -r requirements.txt
```

### 🚪 Para salir del entorno virtual
```bash
deactivate
```



