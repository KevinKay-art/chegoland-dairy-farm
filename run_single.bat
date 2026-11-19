@echo off
cd /d c:\Users\ADMIN\Documents\chegoland\dairy-farm-app
del /f /q test_dairy.db 2>nul
del /f /q dairy_farm.db 2>nul
venv\Scripts\python.exe -m pytest tests/test_admin.py::test_admin_dashboard_access -v > pytest_single.txt 2>&1
type pytest_single.txt
