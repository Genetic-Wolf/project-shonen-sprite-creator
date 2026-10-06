@echo off
cd /d "%~dp0"
if exist "ProjectShonenSpriteCreator.exe" (
 start "" "ProjectShonenSpriteCreator.exe"
 exit /b
)
where py >nul 2>nul
if errorlevel 1 (
 echo This source package has not yet been packaged into the Windows Artist Edition.
 echo The finished Artist Edition runs from ProjectShonenSpriteCreator.exe and does not require Python.
 pause
 exit /b 1
)
py ProjectShonenSpriteCreator.py
