@echo off
cd /d "%~dp0"
if exist "ProjectShonenSpriteCreator.exe" (
 start "" "ProjectShonenSpriteCreator.exe"
 exit /b 0
)
cls
echo PROJECT SHONEN SPRITE CREATOR
echo.
echo The compiled Windows application ProjectShonenSpriteCreator.exe is missing.
echo DO NOT install Python. Python is not required by the Artist Edition.
echo Please use the complete compiled Windows release.
echo.
pause
exit /b 1
