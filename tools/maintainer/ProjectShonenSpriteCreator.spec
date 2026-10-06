# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
datas=[]
for folder in ["assets","masters","templates"]:
    datas.append((folder,folder))
a=Analysis(["ProjectShonenSpriteCreator.py"],
 pathex=[],
 binaries=[],
 datas=datas,
 hiddenimports=["PIL","PIL.Image","PIL.ImageTk","tkinter"],
 hookspath=[],
 hooksconfig={},
 runtime_hooks=[],
 excludes=[],
 noarchive=False)
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,[],exclude_binaries=True,name="ProjectShonenSpriteCreator",debug=False,bootloader_ignore_signals=False,strip=False,upx=True,console=False)
coll=COLLECT(exe,a.binaries,a.datas,strip=False,upx=True,name="ProjectShonenSpriteCreator")
