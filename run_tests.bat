@echo off
cd /d c:\Users\ADMIN\Documents\chegoland\dairy-farm-app
del /f /q test_dairy.db 2>nul
del /f /q dairy_farm.db 2>nul
del /f /q *.db-journal 2>nul
del /f /q *.db-wal 2>nul
del /f /q *.db-shm 2>nul
venv\Scripts\python.exe -m pytest tests/ -v > pytest_out.txt 2>&1
type pytest_out.txt
