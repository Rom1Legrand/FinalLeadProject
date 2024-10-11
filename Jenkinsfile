pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'final-project'
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url:'<https://github.com/Rom1Legrand/FinalLeadProject.git>'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${DOCKER_IMAGE} .'
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

        stage('Run Monitoring') {
            steps {
                script {
                    // Lancer les outils de monitoring
                    sh 'docker run --rm -v "$(pwd):/app" ${DOCKER_IMAGE} python monitor.py'
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
