# Uptime Tray

A tiny Windows system tray app that keeps your uptime visible, so it's never a surprise how long it's been since your last reboot.

## What it does

A colored circle sits in your system tray and reflects how long your PC has been running:

| Uptime            | Icon                                |
|--------------------|--------------------------------------|
| < 24 hours          | Gray circle with a smiley            |
| 1–3 days            | Gray circle with the number of days  |
| 4–7 days            | Orange circle with the number of days|
| > 7 days            | Red circle with the number of days   |

The icon refreshes every 60 seconds.

Clicking the tray icon opens a small menu with two actions:

- **Reboot now** — restarts the computer immediately (after a confirmation prompt)
- **Shutdown at 5** — schedules an automatic shutdown at 17:00 today (or tomorrow if it's already past 17:00), also behind a confirmation prompt

Both actions use the Windows API directly (`ExitWindowsEx` / `InitiateSystemShutdownExW`) rather than shelling out to `shutdown.exe`, which turned out to be unreliable when invoked from a windowed (console-less) process.

## Installing (end users)

Grab `UptimeTray.zip` from the [Releases](../../releases) page (or build it yourself, see below), extract it, and run `install.bat`. This will:

- Copy `UptimeTray.exe` to `%LOCALAPPDATA%\UptimeTray\UptimeTray.exe`
- Add a shortcut to your Startup folder so it launches automatically on login
- Start the app right away

No Python installation is required — the `.exe` is fully standalone.

See `release/README.txt` for detailed install/uninstall instructions (English + Dutch).

## Building from source

Requirements: Python 3.11+, with `pystray`, `Pillow`, `psutil`, and `pyinstaller` installed.

```bash
pip install pystray Pillow psutil pyinstaller
pyinstaller --onefile --noconsole --name "UptimeTray" --clean uptime_tray.py
```

The resulting `dist/UptimeTray.exe` is a standalone executable with no external dependencies.

## Project layout

```
uptime_tray.py    # the app itself
install.bat       # end-user installer (copies exe + sets up autostart)
release/          # packaged zip contents (exe + installer + README.txt)
```

## Logging

The app writes diagnostic info to `%LOCALAPPDATA%\UptimeTray\error.log`, including every menu click, confirmation result, and any Windows API error, which is useful if reboot/shutdown ever silently fails to register with the OS.

## License

Internal tool, no license specified.
