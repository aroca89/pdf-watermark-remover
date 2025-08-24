@echo off
title Verificar Instalacion
echo Verificando instalacion de PDF Watermark Remover...
echo.

if exist "PDF_Watermark_Remover.exe" (
    echo [OK] Ejecutable encontrado
) else (
    echo [ERROR] Ejecutable no encontrado
    goto :error
)

if exist "chromedriver.exe" (
    echo [OK] ChromeDriver encontrado
) else (
    echo [WARNING] ChromeDriver no encontrado
    echo Descarga desde: https://chromedriver.chromium.org/
)

echo.
echo Verificacion completa. Presiona cualquier tecla para probar la aplicacion...
pause > nul

PDF_Watermark_Remover.exe
goto :end

:error
echo.
echo Hay problemas con la instalacion.
pause

:end
