import pytest
import pandas as pd
import boto3
from io import StringIO
import csv

@pytest.fixture
def s3_client():
    return boto3.client('s3')

@pytest.fixture
def s3_dataset(s3_client):
    # Remplacez 'your-bucket-name' et 'your-dataset-key.csv' par les vôtres
    bucket_name = 'your-bucket-name'
    dataset_key = 'your-dataset-key.csv'

    obj = s3_client.get_object(Bucket=bucket_name, Key=dataset_key)
    data = obj['Body'].read().decode('utf-8')
    return pd.read_csv(StringIO(data))

def test_first_10_rows(s3_dataset):
    results = []
    if len(s3_dataset) < 10:
        results.append(["Fail", "moins de 10 lignes dans la base de données"])
        pytest.fail("moins de 10 lignes dans la base de données")
    else:
        first_10 = s3_dataset.head(10)
        if first_10.isnull().values.any():
            empty_cells = first_10[first_10.isnull().any(axis=1)]
            results.append(["Fail", f"erreur, cellules vides aux lignes : {empty_cells.index.tolist()}"])
            pytest.fail(f"erreur, cellules vides aux lignes : {empty_cells.index.tolist()}")
        else:
            results.append(["Pass", "Pas de cellules vides dans les 10 premières lignes"])

    # Écrire les résultats dans un fichier CSV
    with open('test_results.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Status", "Message"])
        writer.writerows(results)