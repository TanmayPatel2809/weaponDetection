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
                        echo "=== Copying GCP key to remote pod ==="
                        scp -P $RUNPOD_SSH_PORT $SSH_OPTS \
                            "$LOCAL_GCP_KEY" \
                            "$RUNPOD_SSH_USER@$RUNPOD_SSH_HOST:/workspace/weapon-detection.json"

                        echo "=== Running remote commands ==="
                        ssh -p $RUNPOD_SSH_PORT $SSH_OPTS \
                            "$RUNPOD_SSH_USER@$RUNPOD_SSH_HOST" << 'ENDSSH'
set -e
echo "Connected successfully"
nvidia-smi || true

cd /workspace

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

export GOOGLE_APPLICATION_CREDENTIALS=/workspace/weapon-detection.json

echo "Starting training pipeline..."
python pipeline/training_pipeline.py
ENDSSH

                        echo "=== Copying results back to Jenkins ==="
                        if [ -d "./weaponDetection" ]; then
                            echo "Local weaponDetection directory exists. Deleting it..."
                            rm -rf "./weaponDetection"
                        fi
                        
                        scp -P $RUNPOD_SSH_PORT $SSH_OPTS -r \
                            "$RUNPOD_SSH_USER@$RUNPOD_SSH_HOST:/workspace/weaponDetection" \
                            "."
                        """
                    }
                }
            }
        }
    }
}