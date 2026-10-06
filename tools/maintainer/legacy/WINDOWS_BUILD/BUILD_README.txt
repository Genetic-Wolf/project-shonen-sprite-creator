MAINTAINER ONLY — NOT PART OF THE FINAL ARTIST EXPERIENCE

This folder exists solely to create the self-contained Windows executable.

Required on the BUILD machine:
- Windows 10/11 x64
- Python
- PyInstaller
- Pillow

The ARTIST machine must not require any of those tools.

BUILD PROCESS
1. Run BUILD_WINDOWS_RC.bat on Windows.
2. Run the acceptance checklist.
3. Copy the resulting ProjectShonenSpriteCreator.exe to the package root.
4. Test the package on a separate/clean Windows account or machine without relying on Python.
5. Only after it passes should the package be labeled Artist Edition.

Do not distribute this maintainer folder to the artist in the final clean package.
