@echo off
setlocal

REM Get current date and time for versioned folder (format: YYYYMMDD-HHMMSS)
for /f "tokens=2 delims==." %%I in ('"wmic os get localdatetime /value"') do set datetime=%%I
set version=%datetime:~0,8%-%datetime:~8,6%

REM Set output folder
set outdir=dist\DSI-service\%version%

REM Create the output folder
mkdir "%outdir%"

REM Build with PyInstaller, outputting to the versioned folder
pyinstaller --add-data "config.json;." --noconsole --clean --distpath "%outdir%" DSI-service.py

echo.
echo Build finished. Output in %outdir%
echo Press any key to exit...
pause
endlocal