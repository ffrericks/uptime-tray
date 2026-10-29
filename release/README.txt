UptimeTray - installation instructions
=======================================

What is this?
--------------
A small program that shows an icon in your system tray (next to the
clock) with your computer's uptime:

- Gray circle with a smiley   -> computer has been on for less than 24 hours
- Gray circle with a number   -> number of days of uptime (1, 2, 3)
- Orange circle with a number -> 4 days or more of uptime
- Red circle with a number    -> more than 7 days of uptime (time to restart)

Click the icon for two options:
- Reboot now     -> restarts the computer immediately (after confirmation)
- Shutdown at 5  -> schedules an automatic shutdown at 17:00
                    (after confirmation; if it's already past 17:00,
                    it schedules it for tomorrow)


Installing
----------
1. Extract this zip fully to a folder on your disk (e.g. Desktop or
   Downloads). Make sure UptimeTray.exe and install.bat stay together
   in the SAME folder.
2. Double-click install.bat
3. A black window briefly appears. Press any key to close it once it
   says "Klaar" / "Done".
4. The icon appears in your system tray. You may need to click the
   arrow (show hidden icons) in the taskbar to see it.

No Python or other installation is required - it works standalone.

The app will from now on start automatically whenever you log in to
Windows.


Note
----
Because UptimeTray.exe is not a digitally signed program, Windows
SmartScreen or your antivirus software may show a warning the very
first time you run it ("unknown publisher" / "Windows protected your
PC"). If this happens, choose "More info" -> "Run anyway". If your
antivirus/EDR software blocks the exe entirely, contact IT.


Uninstalling
------------
1. Close the program via the tray menu (option "Afsluiten" / "Exit"),
   or end the "UptimeTray.exe" process via Task Manager.
2. Delete the folder:
   %LOCALAPPDATA%\UptimeTray
3. Delete the shortcut in the Startup folder:
   %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Uptime Tray.lnk



=======================================
Nederlands
=======================================

UptimeTray - installatie-instructies
=====================================

Wat is dit?
-----------
Een klein programma dat een icoontje in je systray (rechts naast de
klok) laat zien met de uptime van je computer:

- Grijs rondje met smiley  -> computer staat korter dan 24 uur aan
- Grijs rondje met getal   -> aantal dagen uptime (1, 2, 3)
- Oranje rondje met getal  -> 4 dagen of meer uptime
- Rood rondje met getal    -> meer dan 7 dagen uptime (tijd om te herstarten)

Klik op het icoon voor twee opties:
- Reboot now        -> herstart de computer direct (na bevestiging)
- Shutdown at 5      -> plant een automatische shutdown om 17:00 uur in
                        (na bevestiging; is het al na 17:00, dan morgen)


Installeren
-----------
1. Pak deze zip volledig uit naar een map op je schijf (bv. Bureaublad
   of Downloads). Zorg dat UptimeTray.exe en install.bat in DEZELFDE
   map blijven staan.
2. Dubbelklik op install.bat
3. Er verschijnt kort een zwart venster. Druk op een toets om het te
   sluiten zodra er "Klaar" staat.
4. Het icoon verschijnt in je systray. Mogelijk moet je op het pijltje
   (verborgen iconen tonen) klikken in de taakbalk om het te zien.

Er is geen Python of andere installatie nodig - het werkt standalone.

De app start voortaan automatisch op wanneer je inlogt op Windows.


Let op
------
Omdat UptimeTray.exe geen digitaal ondertekend programma is, kan
Windows SmartScreen of je antivirusprogramma bij de allereerste keer
een waarschuwing tonen ("onbekende uitgever" / "Windows heeft je pc
beschermd"). Kies in dat geval voor "Meer informatie" -> "Toch
uitvoeren". Als je antivirus/EDR software de exe blokkeert, neem dan
contact op met IT.


Verwijderen
-----------
1. Sluit het programma af via het systray-menu (optie "Afsluiten"),
   of beeindig het proces "UptimeTray.exe" via Taakbeheer.
2. Verwijder de map:
   %LOCALAPPDATA%\UptimeTray
3. Verwijder de snelkoppeling in de Startup-map:
   %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Uptime Tray.lnk
