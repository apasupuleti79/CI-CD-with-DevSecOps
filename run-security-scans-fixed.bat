@echo off 
venv\Scripts\activate.bat 
echo [INFO] Running Bandit scan... 
bandit -r src/ -f json -o bandit-report.json 
bandit -r src/ -f txt -o bandit-report.txt 
echo [INFO] Running Safety check... 
safety check --json > safety-report.json 
safety check --output text > safety-report.txt 
echo [SUCCESS] Security scans completed 
