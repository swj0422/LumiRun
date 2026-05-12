@echo off
set "PS_PATH=C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
set "DEPLOY_SCRIPT=%~dp0deploy-windows.bat"

if exist "%PS_PATH%" (
    "%PS_PATH%" -Command "Start-Process -FilePath 'cmd.exe' -ArgumentList '/c ""%DEPLOY_SCRIPT%""' -Verb RunAs"
) else (
    echo ERROR: PowerShell not found!
    echo Please run deploy-windows.bat manually as Administrator.
    pause
)
