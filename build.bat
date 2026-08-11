@echo off
setlocal enabledelayedexpansion

echo =========================================
echo Building TrixOS executables (v1.0.2)
echo =========================================

:: Проверяем наличие иконки
if not exist "TrixOS.ico" (
    echo [WARNING] TrixOS.ico not found! Proceeding without icon.
    set ICON_OPT=
) else (
    set ICON_OPT=--icon=TrixOS.ico
)

:: Проверяем, доступен ли pyinstaller как команда
where pyinstaller >nul 2>nul
if %errorlevel% equ 0 (
    set PYINSTALLER=pyinstaller
) else (
    :: Пробуем через python -m PyInstaller
    python -c "import PyInstaller" >nul 2>nul
    if !errorlevel! equ 0 (
        set PYINSTALLER=python -m PyInstaller
    ) else (
        echo [ERROR] PyInstaller not found. Please install: pip install pyinstaller
        pause
        exit /b 1
    )
)

echo Using: !PYINSTALLER!

:: Build CLI
echo.
echo [1/3] Building TrixOS_CLI.exe...
!PYINSTALLER! --onefile --console !ICON_OPT! TrixOS_CLI.py
if !errorlevel! neq 0 (
    echo [ERROR] CLI build failed.
    pause
    exit /b 1
)

:: Build GUI
echo.
echo [2/3] Building TrixOS_Gui.exe...
!PYINSTALLER! --onefile --noconsole !ICON_OPT! --hidden-import=customtkinter --hidden-import=psutil TrixOS_Gui.py
if !errorlevel! neq 0 (
    echo [ERROR] GUI build failed.
    pause
    exit /b 1
)

:: Build Cloud
echo.
echo [3/3] Building TrixOS_Cloud.exe...
!PYINSTALLER! --onefile --noconsole !ICON_OPT! --hidden-import=customtkinter --hidden-import=psutil TrixOS_Cloud.py
if !errorlevel! neq 0 (
    echo [ERROR] Cloud build failed.
    pause
    exit /b 1
)

echo.
echo =========================================
echo Build completed successfully!
echo Executables are in the 'dist' folder.
echo =========================================
pause