@echo off
py -m pip install --upgrade pyinstaller pillow
py -m PyInstaller --noconfirm --clean --windowed --name ProjectShonenSpriteCreator ProjectShonenSpriteCreator.py
pause
