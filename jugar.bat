@echo off
title Motor Brik - Lanzador
cls

echo ======================================
echo        MOTOR BRIK - LANZADOR
echo ======================================

REM --- PRIORIDAD 1: Ejecutable ---
if exist "dist\motor_runtime.exe" (
    echo Ejecutando version compilada...
    start "" "dist\motor_runtime.exe"
    exit
)

REM --- PRIORIDAD 2: Python ---
echo Ejecutando version Python...
python runtime.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: No se pudo ejecutar runtime.py
    pause
)

exit