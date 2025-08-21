import os
import json
from datetime import datetime
from sqlalchemy import create_engine, text
import pandas as pd

# Ajusta estos datos a tu conexión
DATABASE_URL = "mysql+pymysql://root:LupeSecure_2025@localhost:3306/infomundiF"

# Crear carpeta de backups si no existe
BACKUP_DIR = "backups"
os.makedirs(BACKUP_DIR, exist_ok=True)

def run_etl():
    engine = create_engine(DATABASE_URL)

    with engine.connect() as connection:
        # EXTRAER datos de tabla RAW
        raw_query = text("SELECT * FROM raw_data")
        df_raw = pd.read_sql(raw_query, connection)
        registros_leidos = len(df_raw)

        # TRANSFORMACIÓN
        df_clean = df_raw.copy()

        # Ejemplo de limpieza
        if not df_clean.empty:
            df_clean = df_clean.dropna(how="all")  # Eliminar filas totalmente vacías
            if "nombre" in df_clean.columns:
                df_clean = df_clean[df_clean["nombre"] != ""]
                df_clean["nombre"] = df_clean["nombre"].astype(str).str.strip().str.title()
            if "pais" in df_clean.columns:
                df_clean["pais"] = df_clean["pais"].astype(str).str.upper()
            if "fecha" in df_clean.columns:
                df_clean["fecha"] = pd.to_datetime(df_clean["fecha"], errors="coerce")
                df_clean = df_clean.dropna(subset=["fecha"])

        # 🔥 Reemplazar NaN e infinitos por None
        df_clean = df_clean.replace([float("inf"), float("-inf")], None)
        df_clean = df_clean.where(pd.notnull(df_clean), None)

        registros_limpios = len(df_clean)

        # CARGA en tabla CLEANED (truncate + insert)
        connection.execute(text("TRUNCATE TABLE cleaned_data"))
        if registros_limpios > 0:
            for _, row in df_clean.iterrows():
                connection.execute(text("""
                    INSERT INTO cleaned_data (id, nombre, pais, fecha, valor, fuente)
                    VALUES (:id, :nombre, :pais, :fecha, :valor, :fuente)
                """), {
                    "id": int(row["id"]),
                    "nombre": row["nombre"],
                    "pais": row["pais"],
                    "fecha": row["fecha"].strftime("%Y-%m-%d") if row["fecha"] else None,
                    "valor": float(row["valor"]) if row["valor"] not in [None, ""] else None,
                    "fuente": row["fuente"]
                })
            connection.commit()

        # BACKUP de RAW y CLEANED
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_csv_path = os.path.join(BACKUP_DIR, f"raw_backup_{timestamp}.csv")
        clean_csv_path = os.path.join(BACKUP_DIR, f"cleaned_backup_{timestamp}.csv")

        df_raw.to_csv(raw_csv_path, index=False)
        if registros_limpios > 0:
            df_clean.to_csv(clean_csv_path, index=False)

        # LOG
        log_data = {
            "timestamp": timestamp,
            "registros_leidos": registros_leidos,
            "registros_limpios": registros_limpios,
            "raw_backup": raw_csv_path,
            "cleaned_backup": clean_csv_path if registros_limpios > 0 else None
        }

        log_path = os.path.join(BACKUP_DIR, f"etl_log_{timestamp}.json")
        with open(log_path, "w") as log_file:
            json.dump(log_data, log_file, indent=4)

        print("✅ ETL finalizado correctamente.")
        return log_data
