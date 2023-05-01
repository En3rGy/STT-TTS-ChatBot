@echo off
set "CUSTOM_TEMP_PATH=C:\temp"
mkdir "%CUSTOM_TEMP_PATH%" 2>nul
set "TMP=%CUSTOM_TEMP_PATH%"
set "TEMP=%CUSTOM_TEMP_PATH%"
cd bin
stt.exe
cd ..
pause
