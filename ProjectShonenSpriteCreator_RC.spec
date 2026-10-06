# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
datas=[
 ("master_registry.json","."),
 ("library.json","."),
 ("rpgmaker_export_map.json","."),
 ("assets","assets"),
 ("masters","masters"),
 ("templates","templates"),
 ("ui_thumbnails","ui_thumbnails")
]
a=Analysis(["ProjectShonenSpriteCreator.py"],pathex=[],binaries=[],datas=datas,hiddenimports=["PIL._tkinter_finder"],hookspath=[],hooksconfig={},runtime_hooks=[],excludes=[],noarchive=False)
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,a.binaries,a.datas,[],name="ProjectShonenSpriteCreator",debug=False,bootloader_ignore_signals=False,strip=False,upx=True,console=False,disable_windowed_traceback=False)
