@echo off
powershell.exe -Command "Start-Process -FilePath 'powershell.exe' -ArgumentList '-ExecutionPolicy Bypass -File ""%~dp0deploy-windows.ps1""' -Verb RunAs"
