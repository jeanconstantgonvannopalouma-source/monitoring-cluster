#!/bin/bash

echo "Installation de l'agent..."
cd ../agent

if [ ! -f requirements.txt ]; then
    echo "Erreur : requirements.txt introuvable."
    exit 1
fi

pip install -r requirements.txt

echo "Agent installé."
