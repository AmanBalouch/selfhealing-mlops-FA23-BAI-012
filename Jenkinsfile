pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKERHUB_USER        = 'durmuhammad'
        IMAGE_UNSTABLE        = "${DOCKERHUB_USER}/sentiment-api:unstable"
        IMAGE_STABLE          = "${DOCKERHUB_USER}/sentiment-api:stable"
        KUBECONFIG            = "/var/lib/jenkins/.kube/config"
    }

    stages {

        stage('Fetch') {
            steps {
                checkout scm
            }
        }

        stage('Build and Run') {
            steps {
                sh '''
                    docker build --no-cache -t sentiment-api:local .
                    docker stop sentiment-test || true
                    docker rm   sentiment-test || true
                    docker run -d --name sentiment-test -p 5000:5000 sentiment-api:local
                    sleep 20
                '''
            }
        }

        stage('Unit Test') {
            steps {
                sh '''
                    docker run --rm \
                        --network host \
                        -e BASE_URL=http://localhost:5000 \
                        sentiment-api:local \
                        python -m pytest tests/test_api.py -v
                '''
            }
        }

        stage('UI Test') {
            steps {
                sh '''
                    docker run --rm \
                        --network host \
                        -e APP_URL=http://localhost:5000 \
                        --shm-size=2g \
                        -v $(pwd)/tests:/tests \
                        selenium/standalone-chrome:4.21.0-20240517 \
                        bash -c "pip install pytest selenium requests --quiet && python -m pytest /tests/test_ui.py -v" || true
                '''
            }
        }

        stage('Build and Push') {
            steps {
                sh '''
                    echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin

                    docker build -t ${IMAGE_UNSTABLE} .
                    docker push ${IMAGE_UNSTABLE}

                    git fetch origin stable-fallback
                    git checkout origin/stable-fallback -- app.py
                    docker build -t ${IMAGE_STABLE} .
                    docker push ${IMAGE_STABLE}

                    git checkout HEAD -- app.py
                '''
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                    kubectl apply -f k8s/pvc.yaml
                    kubectl apply -f k8s/blue-deployment.yaml
                    kubectl apply -f k8s/green-deployment.yaml
                    kubectl apply -f k8s/service.yaml
                    kubectl rollout status deployment/sentiment-blue-deployment --timeout=120s
                    kubectl rollout status deployment/sentiment-green-deployment --timeout=120s
                '''
            }
        }

    }

    post {
        always {
            sh 'docker stop sentiment-test || true'
            sh 'docker rm   sentiment-test || true'
        }
    }
}