@echo off
python main-1\main.py > output.log 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Script stopped with an error. Check output.log for details.
    echo Press any key to close or use the X button...
    pause
)