@echo off
echo ========================================
echo    Cryptonote SSL Certificate Generator
echo ========================================
echo.

echo Generating SSL certificates for P2P functionality...

REM Create certs directory if it doesn't exist
if not exist "certs" mkdir certs

REM Generate self-signed certificate for localhost
openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

if %errorlevel% equ 0 (
    echo.
    echo SSL certificates generated successfully!
    echo Location: certs/cert.pem and certs/key.pem
    echo These certificates enable secure P2P communication.
) else (
    echo.
    echo ERROR: Failed to generate SSL certificates.
    echo Make sure OpenSSL is installed and available in PATH.
    pause
    exit /b 1
)

echo.
echo Press any key to continue...
pause >nul