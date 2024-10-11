pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'final-project'
        POSTGRES_HOST = 'postgres'
        POSTGRES_DB = 'neon_db'
        POSTGRES_USER = 'postgres'
        POSTGRES_PASSWORD = 'your_password'
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/Rom1Legrand/FinalLeadProject.git'
            }
        }

    stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${DOCKER_IMAGE} .'
            }
        }

    stage('Wait for PostgreSQL') {
            steps {
                script {
                    // Attendre que PostgreSQL soit prêt
                    sh '''
                    while ! pg_isready -h ${POSTGRES_HOST} -p 5432 -U ${POSTGRES_USER}; do
                        echo "Waiting for PostgreSQL...";
                        sleep 3;
                    done;
                    '''
                }
            }
        

    stage('Run Unit Tests') {
            steps {
                script {
                    sh 'docker run --rm -v "$(pwd):/app" ${DOCKER_IMAGE} pytest test.py --junitxml=unit-tests.xml'
                    sh 'docker cp $(docker ps -alq):/app/test_results.csv ./'
                }
            }
        }


    stage('Run Integration Tests') {
            steps {
                script {
                    // Exécuter les tests d'intégration
                    sh 'docker run --rm -v "$(pwd):/app" ${DOCKER_IMAGE} pytest integration_tests'
                }
            }
        }

    stage('Deploy with Airflow') {
            steps {
                script {
                    // Déploiement avec Airflow
                    sh 'docker run --rm -v "$(pwd):/app" ${DOCKER_IMAGE} airflow deploy'
                }
            }
        }
    }

    stage('Get Ngrok URL') {
            steps {
                script {
                    // Récupérer l'URL Ngrok
                    sh 'curl --silent http://localhost:4040/api/tunnels | jq -r .tunnels[0].public_url'
                }
            }
        }
    }


    post {
        success {
            echo 'Pipeline MLOps completed successfully!'
            // Optionnel : envoyer une notification (Slack/Email)
        }
        failure {
            echo 'Pipeline MLOps failed.'
            // Optionnel : envoyer une notification (Slack/Email)
        }
    }
}
