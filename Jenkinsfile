pipeline {
    agent { label 'docker-agent' }
    stages {

        stage('Setup Remote Pod') {
            steps {
                sshagent(['RUNPOD_SSH_KEY']) {
                    withCredentials([file(credentialsId: 'gcp-key', variable: 'LOCAL_GCP_KEY'),string(credentialsId: 'RUNPOD_SSH_USER', variable: 'RUNPOD_SSH_USER'),
                    string(credentialsId: 'RUNPOD_SSH_HOST', variable: 'RUNPOD_SSH_HOST'),
                    string(credentialsId: 'RUNPOD_SSH_PORT', variable: 'RUNPOD_SSH_PORT')]) {

                        sh """
                        # Copy the GCP JSON key to the remote pod
                        scp -P $RUNPOD_SSH_PORT $LOCAL_GCP_KEY $RUNPOD_SSH_USER@$RUNPOD_SSH_HOST:/workspace/weapon-detection.json
 
                        # SSH into remote pod and run commands
                        ssh -p $RUNPOD_SSH_PORT -o StrictHostKeyChecking=no $RUNPOD_SSH_USER@$RUNPOD_SSH_HOST << 'ENDSSH'

                        echo "Connected successfully"
                        nvidia-smi || true

                        cd /workspace
                        git clone https://github.com/TanmayPatel2809/weaponDetection.git
                        cd weaponDetection

                        # Create and activate virtual environment
                        python3 -m venv venv
                        source venv/bin/activate

                        # Upgrade pip and install package
                        pip install --upgrade pip
                        pip install -e .

                        # Set GCP credentials
                        export GOOGLE_APPLICATION_CREDENTIALS=/workspace/weapon-detection.json

                        python pipeline/training_pipeline.py

                        cd ..

                        ENDSSH

                        scp -P $RUNPOD_SSH_PORT -r $RUNPOD_SSH_USER@$RUNPOD_SSH_HOST:/workspace/weaponDetection ./weaponDetection
                        """
                    }
                }
            }
        }
    }
}
