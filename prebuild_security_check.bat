@echo off
REM Cryptonote Pre-Build Security Validation
REM This script MUST run before any build process
REM If security checks fail, build is ABORTED

echo ========================================
echo 🔒 CRYPTONOTE SECURITY VALIDATION
echo ========================================
echo.

REM Run Python security validation
python security_validator.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ SECURITY VIOLATION DETECTED!
    echo ❌ BUILD ABORTED FOR SECURITY REASONS
    echo ❌ Fix security issues before building
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ SECURITY CHECKS PASSED
echo ✅ Safe to proceed with build
echo.

REM Continue with normal build process
goto :eof