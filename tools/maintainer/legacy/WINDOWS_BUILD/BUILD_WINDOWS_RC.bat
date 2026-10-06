@echo off
setlocal
cd /d "%~dp0"
echo Project Shonen Sprite Creator - Windows Release Candidate Builder
echo.
where py >nul 2>nul
if errorlevel 1 (
 echo Python launcher was not found on this MAINTAINER machine.
 pause
 exit /b 1
)
py -m pip install --upgrade pyinstaller pillow
if errorlevel 1 goto :fail
py ReleasePreflight.py
if errorlevel 1 goto :fail
py -m PyInstaller --noconfirm --clean ProjectShonenSpriteCreator_RC.spec
if errorlevel 1 goto :fail
echo.
echo Build complete: dist\ProjectShonenSpriteCreator.exe
echo Copy the EXE into the artist package only after completing WINDOWS_ACCEPTANCE_TEST.md.
pause
exit /b 0
:fail
echo.
echo BUILD/PREFLIGHT FAILED. Do not distribute this release.
pause
exit /b 1
