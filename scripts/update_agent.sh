#!/bin/bash

if [ $# -lt 2 ]; then
    echo "Usage : ./update_agent.sh <agent_name> <fichier_code.py>"
    exit 1
fi

AGENT=$1
FILE=$2

if [ ! -f "$FILE" ]; then
    echo "Erreur : fichier $FILE introuvable."
    exit 1
fi

echo "Envoi de la mise à jour à l'agent $AGENT..."

CODE=$(cat "$FILE")

curl -X POST -H "Content-Type: application/json" \
     -d "{\"code\": \"$CODE\"}" \
     http://localhost:5000/update/$AGENT

echo "Mise à jour envoyée."
