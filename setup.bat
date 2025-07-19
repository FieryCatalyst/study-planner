@echo off
echo ==========================================
echo   Smart Study Planner - First Time Setup
echo ==========================================
echo.

echo 1. Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8 or higher.
    echo    Download from: https://python.org/downloads
    pause
    exit /b 1
)
echo ✅ Python is installed

echo.
echo 2. Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed

echo.
echo 3. Setting up data files...
if not exist "data\users.json" (
    copy "data\users.json.example" "data\users.json" >nul
    echo ✅ Created users.json
) else (
    echo ℹ️  users.json already exists
)

if not exist "data\study_plans.json" (
    copy "data\study_plans.json.example" "data\study_plans.json" >nul
    echo ✅ Created study_plans.json
) else (
    echo ℹ️  study_plans.json already exists
)

if not exist "data\study_progress.csv" (
    copy "data\study_progress.csv.example" "data\study_progress.csv" >nul
    echo ✅ Created study_progress.csv
) else (
    echo ℹ️  study_progress.csv already exists
)

echo.
echo 4. Running system test...
python debug_test.py
if %errorlevel% neq 0 (
    echo ❌ System test failed! Please check the errors above.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo 🎉 SETUP COMPLETE!
echo ==========================================
echo.
echo Your Smart Study Planner is ready to use!
echo.
echo To start the application:
echo   1. Run: run_app.bat
echo   2. Open browser to: http://localhost:5000
echo.
echo For help, see README.md
echo ==========================================
pause
