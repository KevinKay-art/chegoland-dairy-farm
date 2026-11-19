@echo off
cd /d c:\Users\ADMIN\Documents\chegoland\dairy-farm-app
del /f /q test_dairy.db 2>nul
if exist test_dairy.db (
    echo STILL EXISTS
) else (
    echo GONE
)
venv\Scripts\python.exe repro.py
