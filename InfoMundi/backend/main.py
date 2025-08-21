from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from .database import SessionLocal, engine
from .models import Favorito, Base
from pydantic import BaseModel
from .etl_pipeline import run_etl
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
from fastapi.responses import JSONResponse
import math
from sqlalchemy import text
import time

# Crear las tablas en la base de datos (incluye Favorito)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS: permitir conexión con el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar por el origen real en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.on_event("startup")
def wait_for_db():
    for i in range(30):  # ~60s
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ DB lista")
            break
        except Exception as e:
            print(f"⏳ DB no lista ({e}). Reintento {i+1}/30")
            time.sleep(2)
    else:
        raise RuntimeError("❌ DB no estuvo lista a tiempo")



# Dependencia de sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------- FAVORITOS ----------------------

class FavoritoCreate(BaseModel):
    nombre: str
    comentario: str
    imagen_url: str

@app.post("/favoritos")
def crear_favorito(favorito: FavoritoCreate, db: Session = Depends(get_db)):
    nuevo = Favorito(**favorito.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    # 👉 Insertar también en raw_data
    with engine.connect() as conn:
        insert_raw = text("""
            INSERT INTO raw_data (nombre, pais, fecha, valor, fuente)
            VALUES (:nombre, :pais, NOW(), :valor, :fuente)
        """)
        conn.execute(insert_raw, {
            "nombre": favorito.nombre,
            "pais": favorito.nombre,       
            "valor": 0.0,                  
            "fuente": "favorito"
        })
        conn.commit()

    return nuevo

@app.get("/favoritos")
def listar_favoritos(db: Session = Depends(get_db)):
    return db.query(Favorito).all()

# ---- FAVORITOS: obtener por id ----
@app.get("/favoritos/{favorito_id}")
def obtener_favorito(favorito_id: int, db: Session = Depends(get_db)):
    obj = db.query(Favorito).get(favorito_id)
    if not obj:
        return JSONResponse(status_code=404, content={"detail": "No encontrado"})
    return obj

# ---- FAVORITOS: actualizar ----
class FavoritoUpdate(BaseModel):
    nombre: str | None = None
    comentario: str | None = None
    imagen_url: str | None = None

@app.put("/favoritos/{favorito_id}")
def actualizar_favorito(favorito_id: int, cambios: FavoritoUpdate, db: Session = Depends(get_db)):
    obj = db.query(Favorito).get(favorito_id)
    if not obj:
        return JSONResponse(status_code=404, content={"detail": "No encontrado"})
    data = cambios.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

# ---- FAVORITOS: eliminar ----
@app.delete("/favoritos/{favorito_id}")
def eliminar_favorito(favorito_id: int, db: Session = Depends(get_db)):
    obj = db.query(Favorito).get(favorito_id)
    if not obj:
        return JSONResponse(status_code=404, content={"detail": "No encontrado"})
    db.delete(obj)
    db.commit()
    return {"mensaje": "Eliminado"}




# ---------------------- PIPELINE ETL ----------------------

# URL de conexión a DB para uso con pandas/sqlalchemy
DATABASE_URL = "mysql+pymysql://root:LupeSecure_2025@localhost:3306/infomundiF"
engine_direct = create_engine(DATABASE_URL)

# Scheduler automático cada 5 minutos
scheduler = BackgroundScheduler()
scheduler.add_job(run_etl, "interval", minutes=5)  # <-- aquí cambiamos a 5 minutos
scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

@app.post("/api/pipeline/run")
def ejecutar_pipeline():
    log = run_etl()
    return {"mensaje": "ETL ejecutado correctamente", "log": log}

@app.get("/api/cleaned_data")
def obtener_datos_limpios():
    with engine_direct.connect() as connection:
        query = text("SELECT * FROM cleaned_data")
        df = pd.read_sql(query, connection)

        # 🔥 Reemplazar NaN/inf por None antes de serializar
        registros = []
        for _, row in df.iterrows():
            registros.append({
                "id": int(row["id"]) if row["id"] is not None and not pd.isna(row["id"]) else None,
                "nombre": None if pd.isna(row["nombre"]) else row["nombre"],
                "pais": None if pd.isna(row["pais"]) else row["pais"],
                "fecha": row["fecha"].strftime("%Y-%m-%d") if (row["fecha"] is not None and not pd.isna(row["fecha"])) else None,
                "valor": None if (row["valor"] is None or pd.isna(row["valor"]) or (isinstance(row["valor"], float) and math.isinf(row["valor"]))) else float(row["valor"]),
                "fuente": None if pd.isna(row["fuente"]) else row["fuente"]
            })

        return JSONResponse(content=registros)

# ---------------------- Notas de uso ----------------------
# Entorno virtual: python -m venv venv
# Activar Entorno virtual: venv\Scripts\activate
# Ejecutar servidor FastAPI: uvicorn main:app --reload
# Instalar librerías: pip install fastapi uvicorn sqlalchemy pymysql pandas apscheduler
