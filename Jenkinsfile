pipeline {
    agent any

    environment {
        // AWS Settings
        AWS_REGION      = 'ap-south-1'
        CLUSTER_NAME    = 'jenkins-eks-cluster'

        // ECR Settings - replace with your AWS account ID
        AWS_ACCOUNT_ID  = '808999395477'
        ECR_REPO        = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        IMAGE_NAME      = 'jenkins-app'
        IMAGE_TAG       = "${BUILD_NUMBER}"
        FULL_IMAGE      = "${ECR_REPO}/${IMAGE_NAME}:${IMAGE_TAG}"
    }

    stages {

        stage('Checkout Code') {
            steps {
                echo '📥 Pulling code from GitHub...'
                git branch: 'main',
                    credentialsId: 'github-creds',
                    url: 'https://github.com/YOUR_USERNAME/my-jenkins-app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                sh """
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${FULL_IMAGE}
                """
            }
        }

        stage('Push to ECR') {
            steps {
                echo '📤 Pushing image to Amazon ECR...'
                withCredentials([
                    string(credentialsId: 'aws-access-key-id',
                           variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key',
                           variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh """
                        # Login to ECR
                        aws ecr get-login-password \
                          --region ${AWS_REGION} | \
                        docker login \
                          --username AWS \
                          --password-stdin ${ECR_REPO}

                        # Create ECR repo if not exists
                        aws ecr describe-repositories \
                          --repository-names ${IMAGE_NAME} \
                          --region ${AWS_REGION} || \
                        aws ecr create-repository \
                          --repository-name ${IMAGE_NAME} \
                          --region ${AWS_REGION}

                        # Push image
                        docker push ${FULL_IMAGE}

                        echo "✅ Image pushed: ${FULL_IMAGE}"
                    """
                }
            }
        }

        stage('Connect to EKS') {
            steps {
                echo '☸️ Connecting to EKS cluster...'
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

                        echo "✅ Connected to EKS"
                        kubectl get nodes
                    """
                }
            }
        }

        stage('Update K8s Deployment') {
            steps {
                echo '🚀 Deploying to EKS...'
                withCredentials([
                    string(credentialsId: 'aws-access-key-id',
                           variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key',
                           variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh """
                        # Replace image placeholder with actual image
                        sed -i 's|ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/jenkins-app:latest|${FULL_IMAGE}|g' \
                          k8s/deployment.yaml

                        # Apply deployment and service
                        kubectl apply -f k8s/deployment.yaml
                        kubectl apply -f k8s/service.yaml

                        # Wait for rollout to complete
                        kubectl rollout status deployment/jenkins-app \
                          --timeout=120s

                        echo "✅ Deployment successful!"
                    """
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                echo '🔍 Verifying deployment...'
                withCredentials([
                    string(credentialsId: 'aws-access-key-id',
                           variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key',
                           variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh """
                        echo "--- Pods ---"
                        kubectl get pods -l app=jenkins-app

                        echo "--- Service ---"
                        kubectl get svc jenkins-app-service

                        echo "--- App URL ---"
                        kubectl get svc jenkins-app-service \
                          -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
        }
    }

        success {
            echo '''
            ✅ ✅ ✅ DEPLOYMENT SUCCESSFUL ✅ ✅ ✅
            App is running on EKS!
            '''
        }
        failure {
            echo '''
            ❌ ❌ ❌ DEPLOYMENT FAILED ❌ ❌ ❌
        always {
            // Clean up local docker images to save disk space
            sh """
                docker rmi ${IMAGE_NAME}:${IMAGE_TAG} || true
                docker rmi ${FULL_IMAGE} || true
            """
        }
    }
}            '''
        }
            Check console output above for errors.
            Check the Service URL above to access your app.
    post {
            }

