import ctypes
import os
import sys
import threading
import time
import traceback
from datetime import datetime, timedelta

import psutil
from PIL import Image, ImageDraw, ImageFont
import pystray

LOG_DIR = os.path.join(os.environ.get("LOCALAPPDATA", "."), "UptimeTray")
LOG_FILE = os.path.join(LOG_DIR, "error.log")


def log(message):
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - {message}\n")
    except Exception:
        pass

GRAY = (120, 120, 120, 255)
ORANGE = (230, 140, 0, 255)
RED = (210, 40, 40, 255)
WHITE = (255, 255, 255, 255)

SIZE = 64
UPDATE_INTERVAL_SECONDS = 60


def get_uptime_days():
    boot = psutil.boot_time()
    uptime_seconds = time.time() - boot
    return uptime_seconds / 86400.0


def pick_color(days_floor):
    if days_floor >= 8:
        return RED
    if days_floor >= 4:
        return ORANGE
    return GRAY


def make_icon_image(uptime_days):
    days_floor = int(uptime_days)
    color = pick_color(days_floor) if days_floor >= 1 else GRAY

    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = 2
    draw.ellipse([margin, margin, SIZE - margin, SIZE - margin], fill=color)

    if days_floor < 1:
        # smiley face
        eye_r = 4
        draw.ellipse([20, 22, 20 + eye_r * 2, 22 + eye_r * 2], fill=WHITE)
        draw.ellipse([44 - eye_r * 2, 22, 44, 22 + eye_r * 2], fill=WHITE)
        draw.arc([16, 24, 48, 52], start=20, end=160, fill=WHITE, width=4)
    else:
        text = str(days_floor)
        font = None
        for name in ("arialbd.ttf", "arial.ttf"):
            try:
                font = ImageFont.truetype(name, 36)
                break
            except OSError:
                continue
        if font is None:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            ((SIZE - w) / 2 - bbox[0], (SIZE - h) / 2 - bbox[1]),
            text,
            fill=WHITE,
            font=font,
        )

    return img


_MessageBoxW = ctypes.windll.user32.MessageBoxW
_MessageBoxW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint]
_MessageBoxW.restype = ctypes.c_int


def confirm(title, message):
    MB_YESNO = 0x04
    MB_ICONQUESTION = 0x20
    MB_TOPMOST = 0x40000
    MB_SETFOREGROUND = 0x10000
    IDYES = 6
    log(f"confirm() opening dialog: {title!r}")
    result = _MessageBoxW(
        None,
        message,
        title,
        MB_YESNO | MB_ICONQUESTION | MB_TOPMOST | MB_SETFOREGROUND,
    )
    log(f"confirm() dialog closed, result={result}")
    return result == IDYES


from ctypes import wintypes

_advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
_user32 = ctypes.WinDLL("user32", use_last_error=True)

TOKEN_ADJUST_PRIVILEGES = 0x0020
TOKEN_QUERY = 0x0008
SE_PRIVILEGE_ENABLED = 0x0002
EWX_REBOOT = 0x02
EWX_FORCEIFHUNG = 0x10
SHTDN_REASON_MAJOR_OTHER = 0x00000000
SHTDN_REASON_FLAG_PLANNED = 0x80000000


class LUID(ctypes.Structure):
    _fields_ = [("LowPart", wintypes.DWORD), ("HighPart", wintypes.LONG)]


class LUID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("Luid", LUID), ("Attributes", wintypes.DWORD)]


class TOKEN_PRIVILEGES(ctypes.Structure):
    _fields_ = [("PrivilegeCount", wintypes.DWORD), ("Privileges", LUID_AND_ATTRIBUTES * 1)]


_kernel32.GetCurrentProcess.restype = wintypes.HANDLE
_kernel32.GetCurrentProcess.argtypes = []
_kernel32.CloseHandle.restype = wintypes.BOOL
_kernel32.CloseHandle.argtypes = [wintypes.HANDLE]

_advapi32.OpenProcessToken.restype = wintypes.BOOL
_advapi32.OpenProcessToken.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.HANDLE),
]
_advapi32.LookupPrivilegeValueW.restype = wintypes.BOOL
_advapi32.LookupPrivilegeValueW.argtypes = [
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    ctypes.POINTER(LUID),
]
_advapi32.AdjustTokenPrivileges.restype = wintypes.BOOL
_advapi32.AdjustTokenPrivileges.argtypes = [
    wintypes.HANDLE,
    wintypes.BOOL,
    ctypes.POINTER(TOKEN_PRIVILEGES),
    wintypes.DWORD,
    ctypes.c_void_p,
    ctypes.c_void_p,
]
_advapi32.InitiateSystemShutdownExW.restype = wintypes.BOOL
_advapi32.InitiateSystemShutdownExW.argtypes = [
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.DWORD,
    wintypes.BOOL,
    wintypes.BOOL,
    wintypes.DWORD,
]
_advapi32.AbortSystemShutdownW.restype = wintypes.BOOL
_advapi32.AbortSystemShutdownW.argtypes = [wintypes.LPCWSTR]
_user32.ExitWindowsEx.restype = wintypes.BOOL
_user32.ExitWindowsEx.argtypes = [wintypes.UINT, wintypes.DWORD]


def _win_error(label):
    code = ctypes.get_last_error()
    return f"{label} failed: WinError {code} ({ctypes.FormatError(code)})"


def enable_shutdown_privilege():
    hToken = wintypes.HANDLE()
    if not _advapi32.OpenProcessToken(
        _kernel32.GetCurrentProcess(),
        TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY,
        ctypes.byref(hToken),
    ):
        raise OSError(_win_error("OpenProcessToken"))
    try:
        luid = LUID()
        if not _advapi32.LookupPrivilegeValueW(
            None, "SeShutdownPrivilege", ctypes.byref(luid)
        ):
            raise OSError(_win_error("LookupPrivilegeValueW"))
        tp = TOKEN_PRIVILEGES()
        tp.PrivilegeCount = 1
        tp.Privileges[0].Luid = luid
        tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED
        if not _advapi32.AdjustTokenPrivileges(
            hToken, False, ctypes.byref(tp), 0, None, None
        ):
            raise OSError(_win_error("AdjustTokenPrivileges"))
        if ctypes.get_last_error() != 0:
            # AdjustTokenPrivileges can return True but still fail partially
            pass
    finally:
        _kernel32.CloseHandle(hToken)


def win_reboot_now():
    enable_shutdown_privilege()
    ok = _user32.ExitWindowsEx(
        EWX_REBOOT | EWX_FORCEIFHUNG,
        SHTDN_REASON_MAJOR_OTHER | SHTDN_REASON_FLAG_PLANNED,
    )
    if not ok:
        raise OSError(_win_error("ExitWindowsEx"))
    log("ExitWindowsEx (reboot) succeeded")


def win_schedule_shutdown(seconds):
    enable_shutdown_privilege()
    ok = _advapi32.InitiateSystemShutdownExW(
        None,
        None,
        wintypes.DWORD(seconds),
        False,  # bForceAppsClosed
        False,  # bRebootAfterShutdown
        SHTDN_REASON_MAJOR_OTHER | SHTDN_REASON_FLAG_PLANNED,
    )
    if not ok:
        raise OSError(_win_error("InitiateSystemShutdownExW"))
    log(f"InitiateSystemShutdownExW scheduled in {seconds}s")


def win_abort_shutdown():
    enable_shutdown_privilege()
    ok = _advapi32.AbortSystemShutdownW(None)
    if not ok:
        code = ctypes.get_last_error()
        log(f"AbortSystemShutdownW: nothing to abort or failed (WinError {code})")
    else:
        log("AbortSystemShutdownW succeeded")


def _reboot_now_worker():
    try:
        log("Reboot now clicked")
        if not confirm("Reboot now", "Computer nu herstarten?"):
            log("Reboot now: cancelled by user")
            return
        win_reboot_now()
    except Exception:
        log("Reboot now FAILED:\n" + traceback.format_exc())


def reboot_now(icon, item):
    threading.Thread(target=_reboot_now_worker, daemon=True).start()


def _shutdown_at_5_worker():
    try:
        log("Shutdown at 5 clicked")
        if not confirm(
            "Shutdown at 5",
            "Computer vandaag om 17:00 uur automatisch laten afsluiten?",
        ):
            log("Shutdown at 5: cancelled by user")
            return
        now = datetime.now()
        target = now.replace(hour=17, minute=0, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        seconds = int((target - now).total_seconds())
        # cancel any previously scheduled shutdown first
        win_abort_shutdown()
        win_schedule_shutdown(seconds)
    except Exception:
        log("Shutdown at 5 FAILED:\n" + traceback.format_exc())


def shutdown_at_5(icon, item):
    threading.Thread(target=_shutdown_at_5_worker, daemon=True).start()


def quit_app(icon, item):
    icon.stop()


def run():
    log("App gestart")
    icon = pystray.Icon(
        "uptime_tray",
        make_icon_image(get_uptime_days()),
        "Uptime",
        menu=pystray.Menu(
            pystray.MenuItem("Reboot now", reboot_now),
            pystray.MenuItem("Shutdown at 5", shutdown_at_5),
            pystray.MenuItem("Afsluiten", quit_app),
        ),
    )

    def updater():
        while True:
            try:
                days = get_uptime_days()
                icon.icon = make_icon_image(days)
                icon.title = f"Uptime: {days:.1f} dagen"
            except Exception:
                log("Updater FAILED:\n" + traceback.format_exc())
            time.sleep(UPDATE_INTERVAL_SECONDS)

    threading.Thread(target=updater, daemon=True).start()
    icon.run()


if __name__ == "__main__":
    try:
        run()
    except Exception:
        log("Fatale fout bij opstarten:\n" + traceback.format_exc())
