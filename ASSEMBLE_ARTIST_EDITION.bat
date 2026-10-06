@echo off
setlocal
cd /d "%~dp0\.."
if not exist "_MAINTAINER_WINDOWS_BUILD\dist\ProjectShonenSpriteCreator.exe" (
 echo ERROR: Windows EXE has not been built.
 pause
 exit /b 1
)
set OUT=Project-Shonen-Sprite-Creator-Windows-Artist-Edition
if exist "%OUT%" rmdir /s /q "%OUT%"
mkdir "%OUT%"
copy "_MAINTAINER_WINDOWS_BUILD\dist\ProjectShonenSpriteCreator.exe" "%OUT%\ProjectShonenSpriteCreator.exe" >nul
copy "Launch Project Shonen Sprite Creator.bat" "%OUT%\" >nul
copy "ARTIST_README.txt" "%OUT%\" >nul
copy "WINDOWS_DISTRIBUTION_MANIFEST.json" "%OUT%\" >nul
for %%D in (character_projects artist_workspace exports backups) do mkdir "%OUT%\%%D"
echo.
echo Artist Edition folder assembled at:
echo %CD%\%OUT%
echo.
echo Run the clean-machine acceptance test before distribution.
pause
