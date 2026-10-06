@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
 echo This is the source/development package.
 echo The final artist distribution will package this interface as ProjectShonenSpriteCreator.exe.
 echo Artists will not need Python in the packaged Windows release.
 pause
 exit /b 1
)
py ProjectShonenAssetStudio.py
