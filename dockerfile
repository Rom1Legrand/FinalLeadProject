# Utiliser l'image de base Miniconda
FROM continuumio/miniconda3:4.8.2

# Définir le répertoire de travail
WORKDIR /home/app

# Mettre à jour les sources de package pour éviter l'erreur 'Suite' obsolète
RUN apt-get update --allow-releaseinfo-change && apt-get install -y \
    nano unzip curl git

# Installer AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip aws

# Copier le fichier des dépendances
COPY requirements.txt /dependencies/requirements.txt

# Installer les dépendances Python
RUN pip install --no-cache-dir -r /dependencies/requirements.txt && \
    pip install scikit-learn  # Installer scikit-learn explicitement pour éviter les problèmes de version

# Copier les scripts nécessaires dans le répertoire de travail
COPY ./scripts/mlflow_model_training.py /home/app/mlflow_model_training.py

# Copier les datasets nécessaires
COPY ./Data-notebook/covtype_80.csv /home/app/data/covtype_80.csv

# Copier le script secrets.sh
COPY ./scripts/secrets.sh /home/app/secrets.sh
RUN chmod +x /home/app/secrets.sh

# Exposer le port 7860 pour MLflow et Flask
EXPOSE 7860

# Commande par défaut pour lancer le script Python (géré par Docker Compose)
CMD ["python", "/home/app/mlflow_model_training.py"]













