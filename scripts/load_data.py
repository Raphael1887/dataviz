import pandas as pd
import os
import sys
import time
import random
from datetime import datetime, timedelta
from sqlalchemy import text, inspect

# Ajout du dossier parent au path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import get_engine

# --- 1. CHARGEMENT DES JO (Données Réelles) ---
def load_olympic_data(engine):
    csv_path = os.path.join('data', 'athlete_events.csv')
    TABLE_NAME = 'athlete_events'
    
    inspector = inspect(engine)
    if inspector.has_table(TABLE_NAME):
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}"))
            count = result.scalar()
        if count > 0:
            print(f"Table '{TABLE_NAME}' déjà remplie ({count} lignes). Skip.")
            return

    if not os.path.exists(csv_path):
        print("Fichier CSV introuvable pour les JO.")
        return

    print("Chargement des données Olympiques...")
    df = pd.read_csv(csv_path)
    df['Medal'] = df['Medal'].fillna('None')
    df.to_sql(TABLE_NAME, engine, if_exists='replace', index=False, chunksize=1000)
    print("Données Olympiques chargées.")

# --- 2. DONNÉES ADMIN (Fictives) ---
def generate_and_load_admin_data(engine):
    TABLE_NAME = 'admin_metrics'
    
    inspector = inspect(engine)
    if inspector.has_table(TABLE_NAME):
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}"))
            count = result.scalar()
        if count > 0:
            print(f"Table '{TABLE_NAME}' déjà remplie. Skip.")
            return

    print("Génération des données Administrateur...")
    dates = [datetime.today() - timedelta(days=i) for i in range(30)]
    dates.sort()
    
    data = {
        'date': dates,
        'active_users': [random.randint(50, 500) for _ in range(30)],
        'new_signups': [random.randint(0, 20) for _ in range(30)],
        'server_errors': [random.randint(0, 10) for _ in range(30)],
        'avg_response_time_ms': [random.uniform(100, 800) for _ in range(30)]
    }
    pd.DataFrame(data).to_sql(TABLE_NAME, engine, if_exists='replace', index=False)
    print("Données Admin chargées.")

# --- 3. DONNÉES DÉVELOPPEUR (Fictives - NOUVEAU) ---
def generate_and_load_dev_data(engine):
    TABLE_NAME = 'dev_metrics'
    
    inspector = inspect(engine)
    if inspector.has_table(TABLE_NAME):
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}"))
            count = result.scalar()
        if count > 0:
            print(f"Table '{TABLE_NAME}' déjà remplie. Skip.")
            return

    print("Génération des données Développeur...")
    dates = [datetime.today() - timedelta(days=i) for i in range(30)]
    dates.sort()
    
    data = {
        'date': dates,
        'commits_count': [random.randint(2, 25) for _ in range(30)],       # Activité Git
        'bugs_reported': [random.randint(0, 5) for _ in range(30)],        # Qualité code
        'avg_build_time_sec': [random.uniform(120, 400) for _ in range(30)], # CI/CD
        'cpu_usage_percent': [random.uniform(20, 90) for _ in range(30)],  # Monitoring Serveur
        'memory_usage_percent': [random.uniform(40, 85) for _ in range(30)]
    }
    
    pd.DataFrame(data).to_sql(TABLE_NAME, engine, if_exists='replace', index=False)
    print("Données Développeur chargées.")

# --- MAIN ---
def main_load():
    engine = None
    retries = 0
    while retries < 15:
        engine = get_engine()
        if engine:
            try:
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                print("Connecté à PostgreSQL !")
                break
            except Exception:
                pass
        print("En attente de la BDD...")
        time.sleep(2)
        retries += 1
    
    if not engine:
        sys.exit(1)

    load_olympic_data(engine)
    generate_and_load_admin_data(engine)
    generate_and_load_dev_data(engine) # <-- Appel de la nouvelle fonction

if __name__ == "__main__":
    main_load()