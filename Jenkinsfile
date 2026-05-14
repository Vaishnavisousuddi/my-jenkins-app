pipeline {
    agent any

    environment {
        AWS_REGION     = 'ap-south-1'
        CLUSTER_NAME   = 'jenkins-eks-cluster'
        AWS_ACCOUNT_ID = '808999395477'
        ECR_REPO       = "${AWS_ACCOUNT_ID}.dkr.ecr.ap-south-1.amazonaws.com"
        IMAGE_NAME     = 'jenkins-app'
        IMAGE_TAG      = "${BUILD_NUMBER}"
        FULL_IMAGE     = "${AWS_ACCOUNT_ID}.dkr.ecr.ap-south-1.amazonaws.com/jenkins-app:${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main',
                    credentialsId: 'github-creds',
                    url: 'https://github.com/Vaishnavisousuddi/my-jenkins-app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${FULL_IMAGE} ."
            }
        }

        stage('Push to ECR') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id',
                           variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key',
                           variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh """
                        aws ecr get-login-password --region ${AWS_REGION} | \
                        docker login --username AWS \
                        --password-stdin ${ECR_REPO}

                        aws ecr describe-repositories \
                          --repository-names ${IMAGE_NAME} \
                          --region ${AWS_REGION} || \
                        aws ecr create-repository \
                          --repository-name ${IMAGE_NAME} \
                          --region ${AWS_REGION}

                        docker push ${FULL_IMAGE}
                    """
                }
            }
        }

        stage('Deploy to EKS') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id',
                           variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key',
                           variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh """
                        aws eks update-kubeconfig \
                          --region ${AWS_REGION} \
                          --name ${CLUSTER_NAME}

                        kubectl get nodes

                        sed -i 's|IMAGE_PLACEHOLDER|${FULL_IMAGE}|g' \
                          k8s/deployment.yaml

                        kubectl apply -f k8s/deployment.yaml
                        kubectl apply -f k8s/service.yaml

                        kubectl rollout status deployment/jenkins-app \
                          --timeout=120s
                    """
                }
            }
        }

        stage('Verify') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id',
                           variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key',
                           variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh """
                        kubectl get pods -l app=jenkins-app
                        kubectl get svc jenkins-app-service
                    """
                }
            }
        }
    }

    post {
        success {
            echo 'Deployment Successful!'
        }
        failure {
            echo 'Deployment Failed!'
        }
        always {
            sh "docker rmi ${FULL_IMAGE} || true"
        }
    }
}
