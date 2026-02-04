import os
from sqlalchemy import create_engine

# Si on est dans Docker, on utilise l'URL de l'environnement, sinon localhost (pour vos tests locaux)
# Note: 'db' est le nom du service dans docker-compose
DATABASE_URL = os.getenv(
    'DATABASE_URL', 
    'postgresql://user_olympic:password_olympic@localhost:5432/olympic_db'
)

def get_engine():
    try:
        engine = create_engine(DATABASE_URL)
        return engine
    except Exception as e:
        print(f"Erreur de connexion BDD: {e}")
        return None