@echo off
setlocal
pushd "%~dp0"
if not exist ".venv-standard\Scripts\pythonw.exe" (
    echo Set up the virtual environment first. See README.md.
    popd
    pause
    exit /b 1
)
start "" ".venv-standard\Scripts\pythonw.exe" -m pomodoro
popd
