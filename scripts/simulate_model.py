import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import pandas as pd
import joblib

# Charger le dataset
data = pd.read_csv('/app/data/covtype_80.csv')
X = data.drop('Cover_Type', axis=1)
y = data['Cover_Type']

# Split des données
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Configurer MLflow
mlflow.set_tracking_uri("https://lyeshera-mlflow-server-demo.hf.space/")
mlflow.set_experiment('forest_cover_classification')

# Entraîner et logger le modèle dans MLflow
with mlflow.start_run():
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')

    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("f1_score", f1)
    mlflow.sklearn.log_model(model, "random_forest_model")

    joblib.dump(model, 'random_forest_model.pkl')

print(f"Model training completed with Accuracy: {accuracy:.2f}, F1 Score: {f1:.2f}")
