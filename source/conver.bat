@echo off
title Compilar PNG512Converter
echo ========================================
echo    Compilando PNG512Converter a EXE
echo ========================================
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado.
    pause
    exit /b 1
)

:: Instalar/actualizar PyInstaller
echo Instalando/actualizando PyInstaller...
pip install --upgrade pyinstaller
if errorlevel 1 (
    echo [ERROR] No se pudo instalar PyInstaller.
    pause
    exit /b 1
)

:: Verificar que app.ico exista
if not exist app.ico (
    echo [AVISO] No se encuentra app.ico.
)

:: Limpiar builds anteriores
echo Limpiando builds anteriores...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q *.spec 2>nul

:: Compilar incluyendo el icono como DATA y como ICONO del archivo
echo.
echo Compilando...
pyinstaller --onefile --windowed --icon=app.ico --add-data "app.ico;." --name "PNG512Converter" app.py

if errorlevel 1 (
    echo [ERROR] Fallo la compilacion.
    pause
    exit /b 1
)

echo.
echo ========================================
echo ¡Compilacion exitosa!
echo El ejecutable se encuentra en: dist\PNG512Converter.exe
echo ========================================
pause