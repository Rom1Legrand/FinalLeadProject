import boto3
from botocore.exceptions import ClientError

def test_s3_access():
    bucket_name = 'final-project-jedha-team-anne'
    file_content = "Test de création de fichier dans le bucket."
    file_name = "test_upload.txt"

    s3_client = boto3.client('s3', region_name='eu-north-1')

    try:
        s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=file_content)
        print("Upload réussi ! Le bucket est accessible.")
        return True
    except ClientError as e:
        print(f"Erreur d'accès au bucket : {e}")
        return False

# Exécuter le test
if test_s3_access():
    print("Accès S3 validé.")
else:
    print("Accès S3 échoué.")




