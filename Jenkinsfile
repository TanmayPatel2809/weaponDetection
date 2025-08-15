pipeline {
    agent { label 'docker-agent' }

    environment {
        SSH_OPTS = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
    }

    stages {
        stage('Setup Remote Pod') {
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
                        ssh -p $RUNPOD_SSH_PORT $SSH_OPTS \
                            "$RUNPOD_SSH_USER@$RUNPOD_SSH_HOST" 'mkdir -p /temp_workspace'

                        echo "=== Copying GCP key to remote pod ==="
                        scp -P $RUNPOD_SSH_PORT $SSH_OPTS \
                            "$LOCAL_GCP_KEY" \
                            "$RUNPOD_SSH_USER@$RUNPOD_SSH_HOST:/temp_workspace/weapon-detection.json"

                        echo "=== Running remote commands ==="
                        ssh -p $RUNPOD_SSH_PORT $SSH_OPTS \
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
                        
                        scp -P $RUNPOD_SSH_PORT $SSH_OPTS -r \
                            "$RUNPOD_SSH_USER@$RUNPOD_SSH_HOST:/temp_workspace/weaponDetection" \
                            "."
                        echo "=== Complete ==="
                        """
                        
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