import pytest
import pandas as pd
import psycopg2
import os
import csv

@pytest.fixture
def db_connection():
    conn = psycopg2.connect(
        host=os.environ['POSTGRES_HOST'],
        database=os.environ['POSTGRES_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD']
    )
    yield conn
    conn.close()

@pytest.fixture
def db_dataset(db_connection):
    query = "SELECT * FROM your_table_name;"
    df = pd.read_sql_query(query, db_connection)
    return df

def test_first_10_rows(db_dataset):
    results = []
    if len(db_dataset) < 10:
        results.append(["Fail", "moins de 10 lignes dans la base de données"])
        pytest.fail("moins de 10 lignes dans la base de données")
    else:
        first_10 = db_dataset.head(10)
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
