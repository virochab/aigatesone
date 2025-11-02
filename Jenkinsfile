pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.9'
        VENV_PATH = "${WORKSPACE}\\.venv"
        ACTIVATE_SCRIPT = "${VENV_PATH}\\Scripts\\Activate.ps1"
        PYTHONIOENCODING = 'utf-8'
        PYTHONUTF8 = '1'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning repository...'
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                script {
                    echo 'Setting up Python virtual environment...'
                    bat """
                        python -m venv ${VENV_PATH}
                        call ${VENV_PATH}\\Scripts\\activate.bat
                        python -m pip install --upgrade pip
                    """
                }
            }
        }
        
        stage('Install Dependencies') {
            steps {
                script {
                    echo 'Installing required packages from requirements.txt...'
                    bat """
                        call ${VENV_PATH}\\Scripts\\activate.bat
                        pip install -r requirements.txt
                    """
                }
            }
        }
        
        stage('Run Fairness Tests') {
            steps {
                script {
                    echo 'Executing fairness gate tests...'
                    bat """
                        call ${VENV_PATH}\\Scripts\\activate.bat
                        cd /d ${WORKSPACE}
                        python -m pytest tests/test_fairnessGate.py -v --tb=short --junitxml=reports/test-results.xml
                    """
                }
            }
        }
        
        stage('Publish Test Results') {
            steps {
                script {
                    echo 'Publishing test results and reports...'
                    // Archive test reports if they exist
                    bat """
                        if exist reports (
                            echo Archiving JSON and CSV reports...
                            dir /b reports\\*.json
                            dir /b reports\\*.csv
                        )
                    """
                    publishHTML([
                        reportName: 'Fairness Test Report',
                        reportDir: 'reports',
                        reportFiles: '*.html',
                        keepAll: true,
                        alwaysLinkToLastBuild: true
                    ])
                }
            }
        }
        
        stage('Archive Artifacts') {
            steps {
                echo 'Archiving build artifacts...'
                archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
            }
        }
    }
    
    post {
        always {
            junit 'reports/test-results.xml'
            script {
                echo 'Cleaning up...'
                bat """
                    echo Pipeline execution completed
                """
            }
        }
        success {
            echo '✅ Fairness tests completed successfully'
        }
        failure {
            echo '❌ Fairness tests failed'
        }
    }
}

