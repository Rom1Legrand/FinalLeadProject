<<<<<<< HEAD
# FinalLeadProject :
Bloc 4

# Project :
https://www.kaggle.com/datasets/uciml/forest-cover-type-dataset

# dataset
https://archive.ics.uci.edu/static/public/31/covertype.zip

# architecture et répartition des tâches
![image](https://github.com/user-attachments/assets/9d68ed23-4086-40dc-bee3-831663eab885)

=======
# Project Overview

This project aims to develop a fully functional MLOps pipeline that automates the entire lifecycle of a machine learning model. The goal is to create a system capable of continuously integrating, deploying, monitoring, and retraining a machine learning model in production.

The project is divided into several key parts, each managed by different team members:

    Kevin: Responsible for data ingestion, model training, and versioning with MLflow.
    Anne: In charge of monitoring and testing using tools like Evidently and Aporia.
    Romain: Focused on production deployment, using Airflow for automated tasks and Streamlit/Flask for dashboard creation.

# Pipeline Architecture

The pipeline follows a multi-stage process as depicted below:

1. Data Ingestion and Preprocessing (Kevin)

    The initial dataset is retrieved from Kaggle and processed into training and test splits.
    Data is sent to S3 for future ingestion and management.

2. Model Training and Versioning (Kevin)

    MLflow is used to train machine learning models (e.g., RandomForest) and log the training runs.
    The models are versioned and tracked in MLflow, with metadata such as accuracy and F1 scores.
    Models are stored in Hugging Face repositories for collaborative work.

3. Monitoring and Testing (Anne)

    Evidently and Aporia are used for monitoring model performance in production.
    Metrics such as accuracy, drift detection, and latency are tracked.
    Jenkins is set up for continuous integration, ensuring that model updates trigger a pipeline to validate and deploy new models.

4. Deployment and Production (Romain)

    Airflow handles scheduling and orchestration, allowing the entire pipeline to be automated.
    Once in production, a dashboard is available via Streamlit or Flask to visualize model predictions and performance metrics in real time.

# Steps to Run the Project Locally
1. Clone the Repository

bash

git clone https://github.com/Rom1Legrand/FinalLeadProject.git
cd project_final

2. Setup the Environment

Ensure that you have Docker and docker-compose installed.

You will need a .env file with the following variables (used for MLflow and AWS configuration):

bash

HF_TOKEN= Your Token ID ?
ARTIFACT_STORE_URI=s3://final-project-team-anne
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
BACKEND_STORE_URI=postgresql://neondb_owner:ecAvHPW7ait0@ep-patient-union-a5nqgcl3.us-east-2.aws.neon.tech/neondb?sslmode=require
PORT=7860

3. Build the Docker Image

bash

docker build -t mlflow-simulation .

4. Run the Docker Container

bash

docker run -it --rm -p 7860:7860 mlflow-simulation

This command will start MLflow and serve the Flask API on port 7860.
5. Access the MLflow UI

Navigate to https://huggingface.co/spaces/Lyeshera/final_project to access the MLflow user interface, where you can track experiments, manage models, and monitor runs.
6. Simulate Model Predictions

Once the model is trained, you can simulate API calls for predictions using the /predict endpoint of the Flask app:

bash

curl -X POST http://localhost:7860/predict -H "Content-Type: application/json" -d '{"feature1": value1, "feature2": value2, ...}'

# Future Work

    Continuous Monitoring: Set up dashboards using Evidently and Aporia for monitoring real-time metrics.
    CI/CD Pipeline: Implement a Jenkins pipeline that triggers on model updates, ensuring continuous deployment.
    Automation with Airflow: Integrate the model retraining and deployment process with Airflow.
>>>>>>> 3c0da3b (Ajout du projet final avec MLflow, Docker, et scripts)
