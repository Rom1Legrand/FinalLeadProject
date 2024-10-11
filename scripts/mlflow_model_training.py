import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
import joblib
from huggingface_hub import HfApi, HfFolder, Repository
import os
import shutil

# Charger le dataset
data = pd.read_csv('/app/covtype_80.csv')
X = data.drop('Cover_Type', axis=1)
y = data['Cover_Type']

# Split des données
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Définir le nom de l'expérience dans MLflow
mlflow.set_experiment('forest_cover_classification')

# Démarrer une session MLflow
with mlflow.start_run():
    # Initialiser le RandomForestClassifier
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    
    # Entraîner le modèle
    model.fit(X_train, y_train)
    
    # Faire des prédictions
    y_pred = model.predict(X_test)
    
    # Évaluer le modèle
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    # Loguer les paramètres et métriques dans MLflow
    mlflow.log_param('n_estimators', 100)
    mlflow.log_param('max_depth', 10)
    mlflow.log_metric('accuracy', accuracy)
    mlflow.log_metric('f1_score', f1)
    
    # Loguer le modèle dans MLflow
    mlflow.sklearn.log_model(model, 'random_forest_model')
    
    # Sauvegarder le modèle avec joblib
    model_filename = 'random_forest_model.pkl'
    joblib.dump(model, model_filename)

    # Récupérer le token Hugging Face
    hf_token = os.getenv('HF_TOKEN')

    # Cloner le dépôt Hugging Face avec le token dans l'URL
    repo_url = f"https://{hf_token}@huggingface.co/spaces/Lyeshera/final_project"
    repo = Repository(local_dir="final_project", clone_from=repo_url, token=hf_token)

    # Tirer les dernières modifications avant de faire un commit
    repo.git_pull()

    # Copier le modèle dans le dépôt Hugging Face
    shutil.copyfile(model_filename, f"final_project/{model_filename}")

    # Configurer l'identité Git avant le commit
    os.system('git config --global user.email "Chatelain.k@laposte.net"')
    os.system('git config --global user.name "Lyeshera"')

    # Ajouter, commit et pousser le modèle sur Hugging Face
    repo.git_add(auto_lfs_track=True)
    repo.git_commit("Add trained Random Forest model")
    repo.git_push()

print(f"Model training completed with Accuracy: {accuracy:.2f} and F1 Score: {f1:.2f}")

# Configurer l'API Flask
app = Flask(__name__)

# Charger le modèle entraîné
model = joblib.load('random_forest_model.pkl')

# Définir la route pour la prédiction
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    input_data = pd.DataFrame(data, index=[0])
    prediction = model.predict(input_data)
    return jsonify({'prediction': int(prediction[0])})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)


