@echo off
setlocal enabledelayedexpansion

echo.
echo  ====================================
echo     Forex Monitor - Startup Script
echo  ====================================
echo.

:: Check for Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado. Instala Python 3.10+
    pause
    exit /b 1
)

:: Check for Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js no encontrado. Instala Node.js 18+
    pause
    exit /b 1
)

:: Get script directory
set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

:: Create data directory if not exists
if not exist "data" mkdir data

echo [1/4] Configurando entorno virtual Python...
if not exist "backend\venv" (
    echo       Creando venv...
    python -m venv backend\venv
)

echo [2/4] Instalando dependencias del backend...
call backend\venv\Scripts\activate.bat
pip install -q -r backend\requirements.txt

echo [3/4] Instalando dependencias del frontend...
cd frontend
if not exist "node_modules" (
    call npm install
) else (
    echo       node_modules ya existe, saltando...
)
cd ..

echo [4/4] Iniciando servidores...
echo.

:: Start backend in new window
start "Forex Monitor - Backend" cmd /k "cd /d "%ROOT_DIR%backend" && call venv\Scripts\activate.bat && uvicorn app.main:app --reload --port 8000"

:: Wait for backend
echo       Esperando backend (3s)...
timeout /t 3 /nobreak > nul

:: Start frontend in new window
start "Forex Monitor - Frontend" cmd /k "cd /d "%ROOT_DIR%frontend" && npm run dev"

:: Wait for frontend
timeout /t 2 /nobreak > nul

echo.
echo  ====================================
echo     Servidores iniciados:
echo  ------------------------------------
echo     Backend:  http://localhost:8000
echo     Frontend: http://localhost:3000
echo     API Docs: http://localhost:8000/docs
echo  ====================================
echo.
echo  Presiona cualquier tecla para abrir el navegador...
pause > nul

start http://localhost:3000

echo.
echo  Para detener: cierra las ventanas de CMD
echo  o ejecuta: stop.bat
echo.
