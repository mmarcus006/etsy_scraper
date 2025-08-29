@echo off
REM Batch file to launch Etsy Scraper GUI on Windows

echo ===============================================
echo Starting Etsy Scraper GUI...
echo ===============================================
echo.

REM Check if uv is available
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: UV is not installed or not in PATH
    echo Please install UV first: https://github.com/astral-sh/uv
    pause
    exit /b 1
)

echo Launching GUI in your browser...
echo.
echo The interface will open at: http://localhost:8501
echo Press Ctrl+C to stop the server
echo.
echo ===============================================
echo.

REM Run the GUI using UV
uv run streamlit run gui.py --server.port 8501 --server.address localhost

pause