@echo off
echo ========================================
echo    Cryptonote Complete Offline Build
echo ========================================
echo.

REM 🔒 CRITICAL SECURITY CHECK - Run before any build process
echo 🔒 Running pre-build security validation...
call "%~dp0..\..\..\prebuild_security_check.bat"
if %errorlevel% neq 0 (
    echo.
    echo ❌ BUILD ABORTED: Security violations detected
    echo ❌ Fix security issues before building
    echo.
    pause
    exit /b 1
)
echo ✅ Security validation passed - proceeding with build
echo.

echo Building Cryptonote with complete offline capabilities...
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Create build directory
mkdir build
mkdir dist

REM Generate SSL certificates for offline P2P
echo Generating SSL certificates...
if not exist "certs" mkdir certs
openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

REM Build the executable with all dependencies
echo Building executable with offline capabilities...
pyinstaller ^
    --onefile ^
    --noconsole ^
    --name "Cryptonote" ^
    --clean ^
    --noupx ^
    --hidden-import=customtkinter ^
    --hidden-import=argon2 ^
    --hidden-import=cryptography ^
    --hidden-import=flask ^
    --hidden-import=werkzeug ^
    --hidden-import=requests ^
    --hidden-import=pywin32 ^
    --hidden-import=win32clipboard ^
    --hidden-import=win32gui ^
    --hidden-import=win32con ^
    --hidden-import=tiktoken ^
    --hidden-import=googleapiclient ^
    --hidden-import=google_auth_oauthlib ^
    --hidden-import=paypalcheckoutsdk ^
    --hidden-import=pillow ^
    --hidden-import=pyperclip ^
    --hidden-import=src.storage ^
    --hidden-import=src.models ^
    --hidden-import=src.crypto ^
    --add-data "certs;." ^
    --add-data "logs;." ^
    --add-data "user_config.json;." ^
    Gui.py

if %errorlevel% neq 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

REM Create the complete offline distribution package
echo Creating offline distribution package...

REM Create distribution directory structure
set DIST_DIR=Releases\Cryptonote_Offline_v1.0.0
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
mkdir "%DIST_DIR%"

REM Copy executable
copy dist\Cryptonote.exe "%DIST_DIR%\"

REM Copy BuildReqs folder
xcopy BuildReqs "%DIST_DIR%\BuildReqs\" /E /I /H /Y

REM Copy generated certificates
if exist "certs" (
    xcopy certs "%DIST_DIR%\certs\" /E /I /H /Y
)

REM Copy logs directory (empty)
if not exist "%DIST_DIR%\logs" mkdir "%DIST_DIR%\logs"

REM Copy default config
copy user_config.json "%DIST_DIR%\"

REM Copy offline documentation
copy BuildReqs\docs\offline_guide.md "%DIST_DIR%\README.md"

REM Create a simple launcher script
echo @echo off > "%DIST_DIR%\Run_Offline.bat"
echo echo Starting Cryptonote in offline mode... >> "%DIST_DIR%\Run_Offline.bat"
echo echo Make sure Ollama is running for AI features: ollama serve >> "%DIST_DIR%\Run_Offline.bat"
echo echo. >> "%DIST_DIR%\Run_Offline.bat"
echo Cryptonote.exe >> "%DIST_DIR%\Run_Offline.bat"
echo pause >> "%DIST_DIR%\Run_Offline.bat"

echo.
echo ========================================
echo        BUILD COMPLETE!
echo ========================================
echo.
echo Offline distribution package created at:
echo %DIST_DIR%
echo.
echo Package includes:
echo - Cryptonote.exe (main application)
echo - SSL certificates for secure P2P
echo - Default configuration
echo - Setup scripts for offline operation
echo - Complete offline documentation
echo.
echo To use offline:
echo 1. Extract the package
echo 2. Run BuildReqs\scripts\setup_offline.bat
echo 3. Install and start Ollama
echo 4. Run Cryptonote.exe
echo.
echo Press any key to continue...
pause >nul