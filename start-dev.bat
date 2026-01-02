@echo off
echo ===================================
echo    Forex Monitor - Dev Server
echo ===================================
echo.

echo Iniciando Backend (Python/FastAPI)...
cd backend
start cmd /k "pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000"
cd ..

echo.
echo Esperando 5 segundos para que el backend inicie...
timeout /t 5 /nobreak > nul

echo.
echo Iniciando Frontend (Next.js)...
cd frontend
start cmd /k "npm install && npm run dev"
cd ..

echo.
echo ===================================
echo Servidores iniciados:
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo ===================================
echo.
pause
