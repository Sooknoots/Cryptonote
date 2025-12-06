@echo off
echo ========================================
echo    Cryptonote Offline Setup
echo ========================================
echo.

echo Setting up Cryptonote for offline operation...
echo.

REM Create necessary directories
if not exist "certs" mkdir certs
if not exist "logs" mkdir logs
if not exist "models" mkdir models

REM Generate SSL certificates if they don't exist
if not exist "certs\cert.pem" (
    echo Generating SSL certificates for secure P2P communication...
    call BuildReqs\scripts\generate_ssl_certs.bat
) else (
    echo SSL certificates already exist.
)

REM Copy default configuration if user config doesn't exist
if not exist "user_config.json" (
    echo Setting up default configuration...
    copy BuildReqs\configs\default_config.json user_config.json
    echo Default configuration created.
) else (
    echo User configuration already exists.
)

REM Create empty log file if it doesn't exist
if not exist "logs\cryptonote.log" (
    echo. > logs\cryptonote.log
    echo Log file initialized.
)

echo.
echo Offline setup complete!
echo.
echo Next steps:
echo 1. Install Ollama for local AI: https://ollama.ai/download
echo 2. Run: ollama pull llama2 (or your preferred model)
echo 3. Start Ollama service: ollama serve
echo 4. Run Cryptonote.exe
echo.
echo Press any key to continue...
pause >nul