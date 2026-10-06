@echo off
cd /d "%~dp0"
if exist ProjectShonenSpriteCreator.exe (
  echo Run the packaged application's internal checks during Windows acceptance testing.
)
py ReleasePreflight.py 2>nul || python ReleasePreflight.py
pause
