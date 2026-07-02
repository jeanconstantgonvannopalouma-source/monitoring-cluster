#!/bin/bash

echo "Installation du serveur de monitoring..."
cd ../server

if [ ! -f requirements.txt ]; then
    echo "Erreur : requirements.txt introuvable."
    exit 1
fi

pip install -r requirements.txt

echo "Installation terminée."
