@echo off
echo.
echo  Deteniendo Forex Monitor...
echo.

:: Kill processes on ports 8000 and 3000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo  Deteniendo backend (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
    echo  Deteniendo frontend (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo  Servidores detenidos.
echo.
pause
