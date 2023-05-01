@echo off
cls
setlocal enabledelayedexpansion

set DATA_OPTION=

for /r ".\etc" %%i in (*.*) do (
	set ABS_PATH=%%~dpi
    set "RELATIVE_PATH=!ABS_PATH:C:\devel\STT-TTS-ChatBot\=!"
	REM set RELATIVE_PATH=!ABS_PATH:%%~n=!
	REM set RELATIVE_PATH=!ABS_PATH:%%~x=!
    set DATA_OPTION=!DATA_OPTION! --add-data "%%i;!RELATIVE_PATH!"
)

set "DATA_OPTION=!DATA_OPTION:\=/!"
cd src
C:\ProgRW\Python311\Scripts\pyinstaller --onefile %DATA_OPTION% --hidden-import pyttsx3.drivers --additional-hooks-dir=.\hook .\stt.py
cd ..

mkdir bin
move .\src\dist\*.exe .\bin

