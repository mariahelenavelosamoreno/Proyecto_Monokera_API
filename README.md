hablar sobre de que se trata y decir que se necesita para ejecutar el proyecto pero si se quiere ver informarcion mas detallada se encuentra en el reporte.md 


# Apache Airflow con Docker

![Airflow Logo](https://airflow.apache.org/images/feature-image.png)

## 🐳 Inicialización de Airflow con Docker

### Requisitos para Windows
Si estás en Windows, necesitarás:
1. Docker Desktop instalado
2. WSL (Windows Subsystem for Linux) activado

🔗 [Descargar Docker Desktop](https://www.docker.com/products/docker-desktop)

### 🚀 Despliegue
Ejecuta el siguiente comando para iniciar el contenedor (se evita correr docker run solo por simplicidad, en cuanto a variables de entorno y configuraciones):
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



