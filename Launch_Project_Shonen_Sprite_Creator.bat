@echo off
cd /d "%~dp0"
py ProjectShonenSpriteCreator.py
if errorlevel 1 python ProjectShonenSpriteCreator.py
