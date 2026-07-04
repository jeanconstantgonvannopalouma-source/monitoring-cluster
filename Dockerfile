FROM python:3.11-slim

# Répertoire de travail
WORKDIR /app

# Copier les dépendances
COPY requirements.txt .

# Outils de build (pour pandas) + install des libs
RUN apt-get update && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

# Railway fournit la variable d'environnement PORT
ENV PORT=8000

# Commande de démarrage : gunicorn sur app.py
# IMPORTANT : ton fichier doit définir "app = Flask(__name__)"
CMD ["sh", "-c", "gunicorn -w 2 -b 0.0.0.0:${PORT} app:app"]
