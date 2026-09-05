@echo off
:: Right-click this file -> Run as administrator
echo Adding hrms.localhost to hosts file...
findstr /C:"hrms.localhost" "%SystemRoot%\System32\drivers\etc\hosts" >nul
if %errorlevel%==0 (
  echo Already present.
) else (
  echo 127.0.0.1 hrms.localhost>> "%SystemRoot%\System32\drivers\etc\hosts"
  echo Added: 127.0.0.1 hrms.localhost
)
echo.
type "%SystemRoot%\System32\drivers\etc\hosts" | findstr hrms
echo.
pause
