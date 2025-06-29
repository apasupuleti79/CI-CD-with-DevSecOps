@echo off 
set PYTHONIOENCODING=utf-8 
venv\Scripts\activate.bat 
echo [INFO] Running unit tests... 
python -m pytest tests/ --cov=src --cov-report=html --junitxml=test-results.xml 
echo [INFO] Starting application... 
echo Open another terminal and test with: 
echo   curl http://localhost:5000/health 
echo   curl http://localhost:5000/api/info 
python src/app.py 
