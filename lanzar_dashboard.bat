@echo off
REM Script para lanzar REDI7 AI Dashboard en Windows

echo ========================================
echo  REDI7 AI v1.0 - Dashboard Profesional
echo ========================================
echo.

REM Activar entorno virtual si existe
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo Entorno virtual activado
) else (
    echo Usando Python del sistema
)

echo.
echo Lanzando dashboard...
echo Abre tu navegador en: http://localhost:8501
echo.
echo Presiona Ctrl+C para detener el servidor
echo ========================================
echo.

streamlit run app_redi7.py

pause
