#!/bin/bash

# Arrêter le script si une commande échoue
set -e

echo "--- DÉMARRAGE DU CONTENEUR ---"

# 1. Lancer le script de chargement de données
# Grâce à notre modification Python, il va gérer l'attente et la vérification tout seul
python scripts/load_data.py

# 2. Lancer l'application principale
echo "--- LANCEMENT DE DASH ---"
exec python app.py