# 🌍 InfoMundi --- Proyecto Final Programación Web

## Descripción

**InfoMundi** es una aplicación web académica que integra **frontend,
backend, base de datos y pipeline ETL**.\
El sistema permite:

-   Buscar países usando la **API de RestCountries**.\
-   Guardar países como **favoritos** en una base de datos MySQL.\
-   Ejecutar un **pipeline ETL** (manual o automático cada 5 minutos)
    que limpia y normaliza los datos.\
-   Generar **respaldos en CSV y logs JSON**.\
-   Visualizar los datos limpios en una tabla desde el frontend.

------------------------------------------------------------------------

## Tecnologías utilizadas

-   **Frontend**: HTML5, CSS3, JavaScript (Fetch API)\
-   **Backend**: FastAPI, Uvicorn\
-   **ORM**: SQLAlchemy\
-   **Base de datos**: MySQL 8\
-   **ETL**: pandas\
-   **Automatización**: APScheduler, Prefect (opcional)\
-   **Gestión de variables**: python-dotenv\
-   **Contenerización**: Docker + Docker Compose

------------------------------------------------------------------------

## Estructura del proyecto

    proyecto_final_programacion_web/
    ├── backend/
    │   ├── main.py             # API con FastAPI
    │   ├── database.py         # Conexión a MySQL (.env)
    │   ├── models.py           # Modelo Favorito
    │   ├── etl_pipeline.py     # Script ETL
    │   └── __init__.py
    ├── frontend/
    │   ├── index.html          # Interfaz web
    │   ├── styles.css          # Estilos
    │   └── script.js           # Lógica JS (fetch APIs)
    ├── pipeline/
    │   ├── backups/            # CSV generados por ETL
    │   └── logs/               # Logs JSON de ETL
    ├── database/
    │   └── crear_infomundi.sql # Script inicial SQL
    ├── requirements.txt        # Dependencias Python
    ├── docker-compose.yml
    ├── Dockerfile
    ├── .env                    # Variables (no subir al repo)
    └── README.md

------------------------------------------------------------------------

## Instalación y ejecución local

### 1. Clonar repositorio

``` bash
git clone https://github.com/usuario/proyecto_final_programacion_web.git
cd proyecto_final_programacion_web
```

### 2. Crear entorno virtual e instalar dependencias

``` bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

### 3. Configurar MySQL

Ejecuta el script de creación:

``` bash
mysql -uroot -p < database/crear_infomundi.sql
```

Agrega un archivo `.env` en la raíz:

    DATABASE_URL=mysql+pymysql://root:<PASSWORD>@localhost:3306/infomundiF
    ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080

### 4. Levantar backend

``` bash
uvicorn backend.main:app --reload
```

Documentación interactiva: <http://127.0.0.1:8000/docs>

### 5. Levantar frontend

-   Con **Live Server** en VSCode → `frontend/index.html`\
-   O sirviendo el frontend desde FastAPI (opcional).

------------------------------------------------------------------------

## Ejecución con Docker Compose

``` bash
docker compose down -v
docker compose up --build
```

-   API: <http://localhost:8000/docs>\
-   Frontend: <http://localhost:8080>

------------------------------------------------------------------------

## Endpoints principales

  Método   Endpoint              Descripción
  -------- --------------------- ------------------------
  GET      `/favoritos`          Lista favoritos
  POST     `/favoritos`          Crear favorito
  GET      `/favoritos/{id}`     Obtener por id
  PUT      `/favoritos/{id}`     Actualizar favorito
  DELETE   `/favoritos/{id}`     Eliminar favorito
  POST     `/api/pipeline/run`   Ejecutar ETL manual
  GET      `/api/cleaned_data`   Devolver datos limpios

------------------------------------------------------------------------

## ETL y respaldos

-   **Automático cada 5 minutos** gracias a APScheduler.\
-   **Ejecución manual** vía `POST /api/pipeline/run`.\
-   Respalda en `pipeline/backups/`:
    -   `raw_backup_YYYYMMDD_HHMMSS.csv`\
    -   `cleaned_backup_YYYYMMDD_HHMMSS.csv`\
    -   `etl_log_YYYYMMDD_HHMMSS.json`

------------------------------------------------------------------------

## Evidencias de cumplimiento

-   API CRUD en FastAPI.\
-   Base de datos inicializada vía script SQL.\
-   Frontend que consume el API y muestra datos.\
-   ETL con pandas + respaldos CSV/JSON.\
-   Automatización con APScheduler y Prefect.\
-   Docker Compose con servicios: DB + API + Frontend.

------------------------------------------------------------------------

## Requisitos

-   Python 3.12\
-   MySQL 8\
-   Docker Desktop (opcional)\
-   Prefect CLI (si se usa orquestación)
