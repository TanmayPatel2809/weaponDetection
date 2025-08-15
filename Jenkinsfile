pipeline {
    agent { label 'docker-agent' }

    environment {
        GCP_PROJECT = credentials('gcp-project-id')
        GCLOUD_PATH = '/var/jenkins_home/google-cloud-sdk/bin'
        IMAGE_NAME = 'weapondetection'
    }

    stages {
        stage('Train Model on Remote Pod') {
            steps {
                sshagent(['RUNPOD_SSH_KEY']) {
                    withCredentials([
                        file(credentialsId: 'gcp-key', variable: 'LOCAL_GCP_KEY'),
                        string(credentialsId: 'RUNPOD_SSH_USER', variable: 'RUNPOD_SSH_USER'),
                        string(credentialsId: 'RUNPOD_SSH_HOST', variable: 'RUNPOD_SSH_HOST'),
                        string(credentialsId: 'RUNPOD_SSH_PORT', variable: 'RUNPOD_SSH_PORT')
                    ]) {
                        sh """
                        echo "=== Creating temporary workspace on remote pod ==="
                        ssh -p $RUNPOD_SSH_PORT -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \\
                            "$RUNPOD_SSH_USER@$RUNPOD_SSH_HOST" 'mkdir -p /temp_workspace'

                        echo "=== Copying GCP key to remote pod ==="
                        scp -P $RUNPOD_SSH_PORT -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \\
                            "$LOCAL_GCP_KEY" \\
                            "$RUNPOD_SSH_USER@$RUNPOD_SSH_HOST:/temp_workspace/weapon-detection.json"

                        echo "=== Running remote commands ==="
                        ssh -p $RUNPOD_SSH_PORT -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \\
                            "$RUNPOD_SSH_USER@$RUNPOD_SSH_HOST" << 'ENDSSH'
set -e
echo "Connected successfully"
nvidia-smi || true
cd /temp_workspace
echo "Cleaning up old repo if exists..."
rm -rf weaponDetection
echo "Cloning repository..."
git clone https://github.com/TanmayPatel2809/weaponDetection.git
cd weaponDetection
echo "Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo "Installing dependencies..."
pip install --upgrade pip
pip install -e .
export GOOGLE_APPLICATION_CREDENTIALS=/temp_workspace/weapon-detection.json
echo "Starting training pipeline..."
python pipeline/training_pipeline.py
echo "Cleaning up unnecessary files before copying back..."
rm -rf /temp_workspace/weaponDetection/artifacts/raw
rm -rf /temp_workspace/weaponDetection/venv
find /temp_workspace/weaponDetection -type d -name "__pycache__" -exec rm -rf {} +
find /temp_workspace/weaponDetection -type d -name "*.egg-info" -exec rm -rf {} +
ENDSSH

                        echo "=== Copying results back to Jenkins ==="
                        if [ -d "./weaponDetection" ]; then
                            echo "Local weaponDetection directory exists. Deleting it..."
                            rm -rf "./weaponDetection"
                        fi
                        
                        scp -P $RUNPOD_SSH_PORT -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r \\
                            "$RUNPOD_SSH_USER@$RUNPOD_SSH_HOST:/temp_workspace/weaponDetection" \\
                            "."
                        echo "=== Complete ==="
                        """
                    }
                }
            }
        }

        stage('Build and Push Docker Image to GCR'){
            steps{
                dir('weaponDetection') {
                    withCredentials([file(credentialsId: 'gcp-key' , variable : 'GOOGLE_APPLICATION_CREDENTIALS')]){
                        script{
                            echo 'Building and Pushing Docker Image to GCR.............'
                            sh '''
                            export PATH=$PATH:${GCLOUD_PATH}
                            gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                            gcloud config set project ${GCP_PROJECT}
                            gcloud auth configure-docker --quiet
                            docker build -t gcr.io/${GCP_PROJECT}/${IMAGE_NAME}:latest .
                            docker push gcr.io/${GCP_PROJECT}/${IMAGE_NAME}:latest 
                            '''
                        }
                    }
                }
            }
        }

        stage('Deploy to Google Cloud Run'){
            steps{
                withCredentials([file(credentialsId: 'gcp-key' , variable : 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'Deploy to Google Cloud Run.............'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud run deploy ${IMAGE_NAME} \\
                            --image=gcr.io/${GCP_PROJECT}/${IMAGE_NAME}:latest \\
                            --no-invoker-iam-check \\
                            --port=8080 \\
                            --cpu=4 \\
                            --memory=16Gi \\
                            --max-instances=3 \\
                            --no-cpu-throttling \\
                            --region=us-central1 \\
                            --gpu=1 \\
                            --gpu-type=nvidia-l4 \\
                            --no-gpu-zonal-redundancy

                        gcloud beta run domain-mappings describe --domain=weapondetection.tanmay-patel.space --region=us-central1 || \
                        gcloud beta run domain-mappings create \
                            --service=${IMAGE_NAME} \
                            --domain=weapondetection.tanmay-patel.space \
                        '''
                    }
                }
            }
        }
    }
    post {
        always {
            echo 'Cleaning up workspace...'
            cleanWs()
        }
    }
}