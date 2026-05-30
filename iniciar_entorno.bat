@echo off
echo ============================================================
echo  SonoraInc - Configuracion del entorno
echo ============================================================

REM 1. Crear entorno virtual si no existe
IF NOT EXIST "%~dp0entornoSonoraInc\Scripts\activate.bat" (
    echo Creando entorno virtual...
    py -m venv "%~dp0entornoSonoraInc"
    IF ERRORLEVEL 1 (
        echo ERROR: No se pudo crear el entorno virtual.
        echo Asegurate de tener Python instalado y en el PATH.
        pause
        exit /b 1
    )
    echo Entorno virtual creado.
) ELSE (
    echo Entorno virtual encontrado.
)

REM 2. Activar entorno
call "%~dp0entornoSonoraInc\Scripts\activate.bat"

REM 3. Instalar dependencias si faltan
echo Verificando dependencias...
pip install -r "%~dp0requirements.txt" --quiet
echo Dependencias listas.

REM 4. Verificar config.json
IF NOT EXIST "%~dp0SonoraIncWeb\config.json" (
    echo.
    echo AVISO: No se encontro config.json
    echo Copia config.example.json a config.json y ajusta tus credenciales.
    echo.
    pause
    exit /b 1
)

echo.
echo Entorno listo. Para iniciar el servidor ejecuta:
echo   cd SonoraIncWeb
echo   python manage.py runserver
echo.
cmd /k
