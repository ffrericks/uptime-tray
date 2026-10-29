@echo off
setlocal

set "TARGETDIR=%LOCALAPPDATA%\UptimeTray"
set "SRC=%~dp0UptimeTray.exe"

if not exist "%SRC%" (
    echo Kan UptimeTray.exe niet vinden naast dit install.bat bestand.
    pause
    exit /b 1
)

if not exist "%TARGETDIR%" mkdir "%TARGETDIR%"
copy /Y "%SRC%" "%TARGETDIR%\UptimeTray.exe" >nul

set "STARTUPDIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VBS=%TEMP%\mkshortcut_uptimetray.vbs"

> "%VBS%" echo Set oWS = WScript.CreateObject("WScript.Shell")
>> "%VBS%" echo sLinkFile = "%STARTUPDIR%\Uptime Tray.lnk"
>> "%VBS%" echo Set oLink = oWS.CreateShortcut(sLinkFile)
>> "%VBS%" echo oLink.TargetPath = "%TARGETDIR%\UptimeTray.exe"
>> "%VBS%" echo oLink.WorkingDirectory = "%TARGETDIR%"
>> "%VBS%" echo oLink.Description = "Uptime tray icon"
>> "%VBS%" echo oLink.Save

cscript //nologo "%VBS%"
del "%VBS%"

echo.
echo Geinstalleerd naar: %TARGETDIR%\UptimeTray.exe
echo Autostart snelkoppeling aangemaakt in Startup-map.
echo De app wordt nu gestart...

start "" "%TARGETDIR%\UptimeTray.exe"

echo.
echo Klaar. Je kunt dit venster sluiten.
pause
