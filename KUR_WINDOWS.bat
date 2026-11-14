@echo off
setlocal
cd /d "%~dp0"
py -3.12 --version
if errorlevel 1 goto error
if not exist ".venv\Scripts\python.exe" py -3.12 -m venv .venv
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error
echo Kurulum tamamlandi. CALISTIR_WINDOWS.bat dosyasini acin.
pause
exit /b 0
:error
echo Kurulum tamamlanamadi. Yukaridaki hatayi ve KURULUM.md dosyasini inceleyin.
pause
exit /b 1
