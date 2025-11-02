# Jenkins Pipeline for Fairness Testing

## Overview
This Jenkinsfile sets up a CI/CD pipeline to execute fairness gate tests using pytest.

## Pipeline Stages

### 1. Checkout
- Clones the repository using SCM checkout

### 2. Setup Python Environment
- Creates a Python 3.9 virtual environment in `${WORKSPACE}\\.venv`
- Upgrades pip to the latest version
- Windows batch script execution using `bat` steps

### 3. Install Dependencies
Installs required packages from `requirements.txt`:
- `pytest>=8.2.0` - Testing framework
- `pytest-html>=4.1.1` - HTML reporting
- `vaderSentiment>=3.3.2` - Sentiment analysis
- `detoxify>=0.5.0` - Toxicity detection
- `sentence-transformers>=2.7.0` - Semantic similarity

### 4. Run Fairness Tests
- Executes `tests/test_fairnessGate.py` with verbose output
- Generates JUnit XML report: `reports/test-results.xml`
- Continues pipeline execution (does not fail on test errors)

### 5. Publish Test Results
- Archives JSON and CSV reports from `reports/` directory
- Publishes HTML test reports to Jenkins
- Publishes JUnit test results for Jenkins test trend visualization

### 6. Archive Artifacts
- Saves all reports as build artifacts

## Prerequisites
- Jenkins server running on **Windows** with Python 3.9+ installed
- Jenkins plugins:
  - Pipeline
  - JUnit Plugin (for test results)
  - HTML Publisher (optional, for HTML reports)
- Python must be accessible from command line (added to PATH)

## Usage

### Option 1: Declarative Pipeline
1. Create a new Pipeline job in Jenkins
2. Configure it to use "Pipeline script from SCM"
3. Select your SCM (Git, GitHub, etc.)
4. Point to the repository containing this Jenkinsfile
5. Build the job

### Option 2: Scripted Pipeline
For more flexibility, you can convert to a scripted pipeline:
```groovy
node {
    stage('Run Tests') {
        sh 'python -m pytest tests/test_fairnessGate.py -v'
    }
}
```

## Environment Variables
- `PYTHON_VERSION`: Python version to use (default: 3.9)
- `VENV_PATH`: Path to virtual environment (default: `${WORKSPACE}/.venv`)

## Test Output
Reports are generated in the `reports/` directory:
- `test-results.xml` - JUnit XML format for Jenkins
- `fairness_scorecard_YYYYMMDD_HHMMSS.csv` - CSV test results
- `fairness_scorecard_YYYYMMDD_HHMMSS.json` - JSON test results
- HTML reports from pytest-html

The JUnit XML report is automatically published to Jenkins and provides:
- Test trend graphs over time
- Historical test result tracking
- Test duration statistics
- Failed test details

## Troubleshooting

### Python version issues
If Python 3.9 is not available, change `PYTHON_VERSION` in the environment section.

### Virtual environment activation
The pipeline uses Windows batch commands:
```bat
call ${VENV_PATH}\Scripts\activate.bat
```

### Test failures
The pipeline continues even if tests fail. To make the build fail on test errors, add error checking to the batch script.

### Missing HTML Publisher plugin
If the `publishHTML` step fails, either:
1. Install the HTML Publisher plugin, or
2. Comment out the publishHTML section

### Windows-specific issues
- **Virtual environment path**: Uses backslashes (`${WORKSPACE}\\.venv`) for Windows paths
- **Batch commands**: All shell commands use `bat` steps instead of `sh`
- **Activation**: Uses `call activate.bat` for virtual environment activation
- **Directory commands**: Uses `cd /d` for directory changes with drive letters
- **File checking**: Uses `if exist` instead of `[ -d ]` for directory checks

## Customization

### Modify requirements.txt
The pipeline uses `requirements.txt` for dependency management. To add more packages, edit `requirements.txt`:
```txt
pytest>=8.2.0
pytest-html>=4.1.1
vaderSentiment>=3.3.2
detoxify>=0.5.0
sentence-transformers>=2.7.0
# Add your packages here
pytest-xdist>=3.0.0
pytest-cov>=4.0.0
```

### Parallel Test Execution
Add `-n auto` for parallel pytest runs (requires pytest-xdist):
```groovy
python -m pytest tests/test_fairnessGate.py -v -n auto
```

### Code Coverage
Add coverage reporting:
```groovy
pip install pytest-cov
python -m pytest tests/test_fairnessGate.py -v --cov=. --cov-report=html
```

## Post Actions
- **always**: Cleanup operations
- **success**: Displays success message
- **failure**: Displays failure message

