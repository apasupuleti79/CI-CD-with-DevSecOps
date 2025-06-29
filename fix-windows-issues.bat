@echo off
REM DevSecOps Pipeline Fix Script for Windows
REM This script applies fixes for common Windows issues

echo ========================================
echo DevSecOps Pipeline Windows Fix Script
echo ========================================
echo.

REM Set UTF-8 encoding
chcp 65001 > nul
set PYTHONIOENCODING=utf-8

echo [INFO] Setting UTF-8 encoding...

REM Check if Docker Desktop is running
echo [INFO] Checking Docker status...
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] Docker is not running
    echo [INFO] Attempting to start Docker Desktop...
    
    REM Try to start Docker Desktop
    if exist "%ProgramFiles%\Docker\Docker\Docker Desktop.exe" (
        start "" "%ProgramFiles%\Docker\Docker\Docker Desktop.exe"
        echo [INFO] Docker Desktop started. Waiting for initialization...
        timeout /t 30 /nobreak >nul
    ) else (
        echo [WARN] Docker Desktop not found. Please install Docker Desktop or skip Docker tests.
    )
) else (
    echo [SUCCESS] Docker is running
)

REM Fix Safety command syntax
echo [INFO] Creating fixed security scan scripts...

REM Create fixed security scan script
echo @echo off > run-security-scans-fixed.bat
echo venv\Scripts\activate.bat >> run-security-scans-fixed.bat
echo echo [INFO] Running Bandit scan... >> run-security-scans-fixed.bat
echo bandit -r src/ -f json -o bandit-report.json >> run-security-scans-fixed.bat
echo bandit -r src/ -f txt -o bandit-report.txt >> run-security-scans-fixed.bat
echo echo [INFO] Running Safety check... >> run-security-scans-fixed.bat
echo safety check --json ^> safety-report.json >> run-security-scans-fixed.bat
echo safety check --output text ^> safety-report.txt >> run-security-scans-fixed.bat
echo echo [SUCCESS] Security scans completed >> run-security-scans-fixed.bat

REM Create application test script
echo @echo off > test-app-fixed.bat
echo set PYTHONIOENCODING=utf-8 >> test-app-fixed.bat
echo venv\Scripts\activate.bat >> test-app-fixed.bat
echo echo [INFO] Running unit tests... >> test-app-fixed.bat
echo python -m pytest tests/ --cov=src --cov-report=html --junitxml=test-results.xml >> test-app-fixed.bat
echo echo [INFO] Starting application... >> test-app-fixed.bat
echo echo Open another terminal and test with: >> test-app-fixed.bat
echo echo   curl http://localhost:5000/health >> test-app-fixed.bat
echo echo   curl http://localhost:5000/api/info >> test-app-fixed.bat
echo python src/app.py >> test-app-fixed.bat

REM Create security report generation script
echo @echo off > generate-security-report-fixed.bat
echo set PYTHONIOENCODING=utf-8 >> generate-security-report-fixed.bat
echo venv\Scripts\activate.bat >> generate-security-report-fixed.bat
echo python security/generate_security_report.py >> generate-security-report-fixed.bat

echo [SUCCESS] Fixed scripts created:
echo   - run-security-scans-fixed.bat
echo   - test-app-fixed.bat  
echo   - generate-security-report-fixed.bat
echo.

REM Run the fixed verification
echo [INFO] Running fixed pipeline verification...
python verify-pipeline-fixed.py

echo.
echo ========================================
echo Windows Fix Script Completed
echo ========================================
echo.
echo Next steps:
echo 1. Review the verification results above
echo 2. Use the fixed batch scripts for individual testing:
echo    - run-security-scans-fixed.bat
echo    - test-app-fixed.bat
echo    - generate-security-report-fixed.bat
echo 3. If Docker tests failed, start Docker Desktop and re-run
echo.

pause
