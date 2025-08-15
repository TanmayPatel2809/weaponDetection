pipeline {
    agent { label 'docker-agent' }

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
                        echo "Copying GCP key to remote pod..."
                        scp -P $RUNPOD_SSH_PORT \
                            -o StrictHostKeyChecking=no \
                            -o UserKnownHostsFile=/dev/null \
                            $LOCAL_GCP_KEY \
                            $RUNPOD_SSH_USER@$RUNPOD_SSH_HOST:/workspace/weapon-detection.json

                        echo "Running commands on remote pod..."
                        ssh -p $RUNPOD_SSH_PORT -o StrictHostKeyChecking=no $RUNPOD_SSH_USER@$RUNPOD_SSH_HOST << 'ENDSSH'

                        echo "Connected successfully"
                        nvidia-smi || true

                        cd /workspace

                        # Remove existing weaponDetection directory if present
                        if [ -d "weaponDetection" ]; then
                            echo "Removing existing weaponDetection directory..."
                            rm -rf weaponDetection
                        fi

                        git clone https://github.com/TanmayPatel2809/weaponDetection.git
                        cd weaponDetection

                        python3 -m venv venv
                        source venv/bin/activate

                        pip install --upgrade pip
                        pip install -e .

                        export GOOGLE_APPLICATION_CREDENTIALS=/workspace/weapon-detection.json

                        python pipeline/training_pipeline.py
                        cd ..
                        ENDSSH

                        echo "Copying results back to Jenkins..."
                        scp -P $RUNPOD_SSH_PORT \
                            -o StrictHostKeyChecking=no \
                            -o UserKnownHostsFile=/dev/null \
                            -r $RUNPOD_SSH_USER@$RUNPOD_SSH_HOST:/workspace/weaponDetection ./weaponDetection
                        """
                    }
                }
            }
        }
    }
}
