import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import pandas as pd
import joblib
import os
import argparse
import logging

# Activer les logs pour diagnostiquer les erreurs
logging.basicConfig(level=logging.DEBUG)

# Parsing des arguments
parser = argparse.ArgumentParser()
parser.add_argument('--n_estimators', type=int, default=100, help='Number of estimators for RandomForest')
parser.add_argument('--max_depth', type=int, default=10, help='Maximum depth for RandomForest')
args = parser.parse_args()

# Définir des valeurs par défaut si les arguments ne sont pas fournis
n_estimators = int(os.getenv('N_ESTIMATORS', args.n_estimators))
max_depth = int(os.getenv('MAX_DEPTH', args.max_depth))

# Configurer le tracking URI et l'expérience
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "https://lyeshera-final-project-mlflow.hf.space"))
experiment_name = "forest_cover_classification_new_v2"

# Vérifier et récupérer l'expérience par son nom
client = mlflow.tracking.MlflowClient()
experiment = client.get_experiment_by_name(experiment_name)
if experiment is None:
    experiment_id = client.create_experiment(experiment_name)
else:
    experiment_id = experiment.experiment_id

print("Chargement du dataset...")
data = pd.read_csv('/home/app/data/covtype_80.csv')
print("Dataset chargé avec succès.")

X = data.drop('Cover_Type', axis=1)
y = data['Cover_Type']

# Split des données
print("Split des données...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Fermer tout run actif pour éviter les conflits
mlflow.end_run()

# Démarrer une session MLflow en utilisant l'ID de l'expérience récupéré
print("Démarrage de la session MLflow...")
with mlflow.start_run(experiment_id=experiment_id):
    print("Entraînement du modèle RandomForestClassifier...")
    model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
    model.fit(X_train, y_train)
    print("Modèle entraîné avec succès.")

    # Faire des prédictions
    print("Prédiction sur le jeu de test...")
    y_pred = model.predict(X_test)

    # Évaluer le modèle
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    # Loguer les paramètres et métriques dans MLflow
    print("Log des paramètres et métriques dans MLflow...")
    mlflow.log_param('n_estimators', n_estimators)
    mlflow.log_param('max_depth', max_depth)
    mlflow.log_metric('accuracy', accuracy)
    mlflow.log_metric('f1_score', f1)
    
    # Loguer le modèle dans MLflow
    print("Log du modèle dans MLflow...")
    mlflow.sklearn.log_model(model, artifact_path="random_forest_model")

    # Sauvegarder le modèle avec joblib
    model_filename = 'random_forest_model.pkl'
    joblib.dump(model, model_filename)
    print("Modèle sauvegardé avec joblib.")

print(f"Model training completed with Accuracy: {accuracy:.2f} and F1 Score: {f1:.2f}")
