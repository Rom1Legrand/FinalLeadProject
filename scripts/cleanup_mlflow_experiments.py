import mlflow
from mlflow.tracking import MlflowClient
import requests
import os

# Assurez-vous que MLFLOW_TRACKING_URI est bien configurée pour Hugging Face
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "https://lyeshera-final-project-mlflow.hf.space"))

client = MlflowClient()

print("Vérification et récupération des expériences depuis Hugging Face...")

# Vérifier que la connexion est bien établie avec Hugging Face
try:
    # Vérifier que la méthode search_experiments est disponible
    all_experiments = client.search_experiments(view_type=mlflow.entities.ViewType.ALL)
except AttributeError:
    print("La méthode `search_experiments` n'est pas disponible. Assurez-vous que MLflow est à jour.")
    exit(1)
except requests.exceptions.ConnectionError:
    print("Erreur de connexion : assurez-vous que le serveur MLflow sur Hugging Face est accessible.")
    exit(1)

# Itérer sur toutes les expériences et restaurer celles en état 'deleted', puis les supprimer définitivement
print("Vérification des statuts des expériences...")
for exp in all_experiments:
    if exp.lifecycle_stage == "deleted":
        print(f"Restauration de l'expérience supprimée : {exp.name} (ID : {exp.experiment_id})")
        client.restore_experiment(exp.experiment_id)
        print(f"Suppression définitive de l'expérience : {exp.name}")
        client.delete_experiment(exp.experiment_id)

print("Nettoyage terminé.")


