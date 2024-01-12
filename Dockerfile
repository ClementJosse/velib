# Utilisez une image Python officielle en tant qu'image parent
FROM python:3.8-slim

# Définir le répertoire de travail sur /app
WORKDIR /app

# Copiez le contenu du répertoire actuel dans le conteneur à /app
COPY . /app

# Installez les packages spécifiés dans requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Exposez le port 8050 pour que l'application soit accessible
EXPOSE 8050

# Définir la variable d'environnement PYTHONUNBUFFERED pour éviter les problèmes d'impression dans le conteneur
ENV PYTHONUNBUFFERED 1

# Exécutez l'application Dash quand le conteneur démarre
CMD ["python", "app.py"]