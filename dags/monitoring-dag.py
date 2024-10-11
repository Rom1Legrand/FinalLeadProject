from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.email import EmailOperator
from airflow.operators.dummy import DummyOperator
from airflow.models import Variable
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
import os
import glob
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from evidently.test_suite import TestSuite
from evidently.tests import TestColumnDrift
from evidently.ui.workspace.cloud import CloudWorkspace



# Variables Airflow
EVIDENTLY_CLOUD_TOKEN = Variable.get("EVIDENTLY_CLOUD_TOKEN") 
EVIDENTLY_CLOUD_PROJECT_ID = Variable.get("EVIDENTLY_CLOUD_PROJECT_ID")

# Chemins des répertoires
DATA_DIR = "/opt/airflow/data"
REFERENCE_DIR = os.path.join(DATA_DIR, "reference")
DATA_DRIFT_DIR = os.path.join(DATA_DIR, "data-drift")
REFERENCE_FILE = os.path.join(REFERENCE_DIR, "covtype_reference_first100.csv")

# Colonnes à analyser
COLUMNS_TO_ANALYZE = [
    "Elevation", "Aspect", "Slope", "Horizontal_Distance_To_Hydrology",
    "Vertical_Distance_To_Hydrology", "Horizontal_Distance_To_Roadways",
    "Hillshade_9am", "Hillshade_Noon", "Hillshade_3pm",
    "Horizontal_Distance_To_Fire_Points"
]

def _load_files(data_logs_filename):
    reference = pd.read_csv(REFERENCE_FILE)
    data_logs = pd.read_csv(data_logs_filename)
    return reference, data_logs

def detect_file(**context):
    data_logs_list = glob.glob(os.path.join(DATA_DRIFT_DIR, "covtype_reference_update*.csv"))
    if not data_logs_list:
        return "no_file_found_task"
    data_logs_filename = max(data_logs_list, key=os.path.getctime)
    context["task_instance"].xcom_push(key="data_logs_filename", value=data_logs_filename)
    return "detect_data_drift_task"


def detect_data_drift(**context):
    """Produces a report on Evidently Cloud, limited to specific columns"""

    # Set up Evidently Cloud workspace
    ws = CloudWorkspace(
        token=EVIDENTLY_CLOUD_TOKEN,
        url="https://app.evidently.cloud"
    )

    # Get the project from Evidently Cloud
    project = ws.get_project(EVIDENTLY_CLOUD_PROJECT_ID)

    # Retrieve the file containing data logs from Airflow's XCom
    data_logs_filename = context["task_instance"].xcom_pull(key="data_logs_filename")

    # Load reference and current data (implement _load_files if needed)
    reference, data_logs = _load_files(data_logs_filename)

    if reference is None or data_logs is None:
        raise ValueError("Failed to load reference or data logs.")

    # Specific columns to analyze for drift detection
    columns_to_analyze = [
        "Elevation", "Aspect", "Slope", "Horizontal_Distance_To_Hydrology",
        "Vertical_Distance_To_Hydrology", "Horizontal_Distance_To_Roadways",
        "Hillshade_9am", "Hillshade_Noon", "Hillshade_3pm",
        "Horizontal_Distance_To_Fire_Points"
    ]

    # Filter data to include only the selected columns
    reference_filtered = reference[columns_to_analyze]
    data_logs_filtered = data_logs[columns_to_analyze]

    # Create the drift report with Evidently's DataDriftPreset
    data_drift_report = Report(metrics=[DataDriftPreset()])

    try:
        # Run the drift report on the filtered data
        data_drift_report.run(current_data=data_logs_filtered, reference_data=reference_filtered)
        ws.add_report(project.id, data_drift_report, include_data=True)
    except Exception as e:
        raise RuntimeError(f"Error generating data drift report: {e}")

    return "prepare_email_content_task"



def prepare_email_content(**context):
    ti = context["task_instance"]
    drift_detected = ti.xcom_pull(key="drift_detected")
    data_logs_filename = ti.xcom_pull(key="data_logs_filename")
    results_summary = ti.xcom_pull(key="results_summary")
    
    # Check if results_summary is None and provide a fallback if necessary
    if results_summary is None:
        results_summary = "Résumé non disponible"  # Default text if results_summary is missing

    if drift_detected:
        subject = "Alerte : Dérive de données détectée"
        body = f"""Une dérive de données a été détectée dans le fichier : {data_logs_filename}<br><br>
                   Résumé des tests :<br>
                   {results_summary.replace('\n', '<br>')}"""
    else:
        subject = "Info : Pas de dérive de données détectée"
        body = f"""Aucune dérive de données significative n'a été détectée dans le fichier : {data_logs_filename}<br><br>
                   Résumé des tests :<br>
                   {results_summary.replace('\n', '<br>')}"""
    
    # Push the email subject and body to XCom
    ti.xcom_push(key="email_subject", value=subject)
    ti.xcom_push(key="email_body", value=body)


def send_email_with_smtp(**context):
    ti = context['ti']
    
    # Récupérer le sujet et le corps de l'email depuis la tâche précédente
    subject = ti.xcom_pull(key='email_subject', task_ids='prepare_email_content_task')
    body = ti.xcom_pull(key='email_body', task_ids='prepare_email_content_task')
    
    # Vérifier si le sujet et le corps sont None
    if subject is None or body is None:
        raise ValueError("Le sujet ou le corps de l'email est manquant.")
    
    to_email = "dsgattaca@gmail.com"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "dsgattaca@gmail.com"
    
    # Récupérer le mot de passe depuis les variables Airflow
    smtp_password = Variable.get("gmail_password", default_var=None)
    if smtp_password is None:
        raise ValueError("Le mot de passe Gmail n'est pas défini dans les variables Airflow.")

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = to_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return f"Email envoyé à {to_email} avec succès !"
    except Exception as e:
        error_message = f"Erreur lors de l'envoi de l'e-mail : {str(e)}"
        print(error_message)  # Log l'erreur
        raise Exception(error_message)  # Relève l'exception pour qu'Airflow la capture

default_args = {
    'owner': 'RL',
    'start_date': datetime(2024, 10, 10),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'detect_data_drift_and_notify',
    default_args=default_args,
    description='Détecte la dérive des données et envoie une notification par email',
    schedule_interval=timedelta(days=1),
)

detect_file_task = BranchPythonOperator(
    task_id='detect_file_task',
    python_callable=detect_file,
    provide_context=True,
    dag=dag,
)

detect_data_drift_task = PythonOperator(
    task_id='detect_data_drift_task',
    python_callable=detect_data_drift,
    provide_context=True,
    dag=dag,
)

prepare_email_content_task = PythonOperator(
    task_id='prepare_email_content_task',
    python_callable=prepare_email_content,
    provide_context=True,
    dag=dag,
)

send_email_task = PythonOperator(
    task_id='send_email_task',
    python_callable=send_email_with_smtp,
    provide_context=True,
    dag=dag,
)

no_file_found_task = DummyOperator(
    task_id='no_file_found_task',
    dag=dag,
)

detect_file_task >> [detect_data_drift_task, no_file_found_task]
detect_data_drift_task >> prepare_email_content_task >> send_email_task