@echo off
setlocal
cd /d "%~dp0"
echo ==========================================================
echo Project Shonen Sprite Creator - Windows Artist Build
echo ==========================================================
echo This file is for the project maintainer, NOT the artist.
echo.
where py >nul 2>nul
if errorlevel 1 (
 echo Python is required only on the computer BUILDING the app.
 echo The finished Artist Edition does not require the artist to install Python.
 pause
 exit /b 1
)
py -m pip install --upgrade pyinstaller pillow
py -m PyInstaller --noconfirm --clean ProjectShonenSpriteCreator.spec
if errorlevel 1 (
 echo Build failed.
 pause
 exit /b 1
)
echo.
echo Build finished in dist\ProjectShonenSpriteCreator
echo Copy the supporting project files and workflow scripts into that folder before distribution.
pause
