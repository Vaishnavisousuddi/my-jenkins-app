pipeline {
    agent any

    environment {
        AWS_REGION     = 'ap-south-1'
        CLUSTER_NAME   = 'jenkins-eks-cluster'
        AWS_ACCOUNT_ID = '808999395477'
        ECR_REPO       = '808999395477.dkr.ecr.ap-south-1.amazonaws.com'
        IMAGE_NAME     = 'jenkins-app'
        IMAGE_TAG      = "${BUILD_NUMBER}"
        FULL_IMAGE     = '808999395477.dkr.ecr.ap-south-1.amazonaws.com/jenkins-app:${BUILD_NUMBER}'
    }

    stages {

        stage('Checkout Code') {
            steps {
                echo 'Pulling code from GitHub...'
                git branch: 'main',
                    credentialsId: 'github-creds',
                    url: 'https://github.com/Vaishnavisousuddi/my-jenkins-app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                sh '''
                    docker build -t $ECR_REPO/$IMAGE_NAME:$IMAGE_TAG .
                '''
            }
        }

        stage('Push to ECR') {
            steps {
                echo 'Pushing image to Amazon ECR...'
                withCredentials([
                    string(credentialsId: 'aws-access-key-id',
                           variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key',
                           variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                        aws ecr get-login-password --region $AWS_REGION | \
                        docker login --username AWS \
                        --password-stdin $ECR_REPO

                        aws ecr describe-repositories \
                          --repository-names $IMAGE_NAME \
                          --region $AWS_REGION || \
                        aws ecr create-repository \
                          --repository-name $IMAGE_NAME \
                          --region $AWS_REGION

                        docker push $ECR_REPO/$IMAGE_NAME:$IMAGE_TAG
                    '''
                }
            }
        }

        stage('Deploy to EKS') {
            steps {
                echo 'Deploying to EKS...'
                sh '''
                    aws eks update-kubeconfig \
                      --region $AWS_REGION \
                      --name $CLUSTER_NAME

                    echo "Connected to EKS - Nodes:"
                    kubectl get nodes

                    sed -i "s|IMAGE_PLACEHOLDER|$ECR_REPO/$IMAGE_NAME:$IMAGE_TAG|g" \
                      k8s/deployment.yaml

                    kubectl apply -f k8s/deployment.yaml
                    kubectl apply -f k8s/service.yaml

                    kubectl rollout status deployment/jenkins-app \
                      --timeout=120s

                    echo "Deployment Done!"
                '''
            }
        }

        stage('Verify') {
            steps {
                echo 'Verifying deployment...'
                sh '''
                    echo "--- Pods ---"
                    kubectl get pods -l app=jenkins-app

                    echo "--- Service ---"
                    kubectl get svc jenkins-app-service

                    echo "--- App URL ---"
                    kubectl get svc jenkins-app-service \
                      -o jsonpath="{.status.loadBalancer.ingress[0].hostname}"
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline Successful! App is live on EKS!'
        }
        failure {
            echo 'Pipeline Failed! Check logs above.'
        }
        always {
            sh 'docker rmi $ECR_REPO/$IMAGE_NAME:$IMAGE_TAG || true'
        }
    }
}
