@echo off 
set PYTHONIOENCODING=utf-8 
venv\Scripts\activate.bat 
python security/generate_security_report.py 
