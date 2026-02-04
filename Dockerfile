# Utiliser une image Python légère officielle
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements d'abord (pour optimiser le cache Docker)
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le reste du projet dans le conteneur
COPY . .

# Suppression du RUN chmod +x entrypoint.sh

EXPOSE 8050

# --- NOUVELLE COMMANDE ---
# Lance bash et lui dit d'exécuter le script, puis le processus app.py
# On ne dépend plus du bit d'exécution du fichier sur l'hôte.
CMD ["/bin/bash", "entrypoint.sh"]