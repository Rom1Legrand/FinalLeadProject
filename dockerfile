# Utiliser l'image de base Miniconda
FROM continuumio/miniconda3

# Définir le répertoire de travail
WORKDIR /home/app

# Installer les outils nécessaires
RUN apt-get update && apt-get install -y \
    nano unzip curl git supervisor

# Installer Deta CLI
RUN curl -fsSL https://get.deta.dev/cli.sh | sh

# Installer AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install

# Copier le fichier des dépendances
COPY requirements.txt /dependencies/requirements.txt

# Installer les dépendances Python
RUN pip install --no-cache-dir -r /dependencies/requirements.txt

# Copier les scripts nécessaires dans le répertoire de travail
COPY ./scripts/mlflow_model_training.py /home/app/mlflow_model_training.py
COPY ./scripts/simulate_model.py /home/app/simulate_model.py

# Copier les datasets nécessaires
COPY ./Data-notebook/covtype_80.csv /home/app/covtype_80.csv

# Copier le script secrets.sh et l'exécuter
COPY ./secrets.sh /home/app/secrets.sh
RUN chmod +x /home/app/secrets.sh && /home/app/secrets.sh

# Copier la configuration de supervisord
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Exposer le port 7860 pour MLflow et Flask
EXPOSE 7860

# Définir les variables d'environnement pour MLflow
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
ENV BACKEND_STORE_URI=$BACKEND_STORE_URI
ENV ARTIFACT_STORE_URI=$ARTIFACT_STORE_URI

# Commande par défaut pour démarrer supervisord qui gère MLflow et Flask
CMD ["/usr/bin/supervisord"]



