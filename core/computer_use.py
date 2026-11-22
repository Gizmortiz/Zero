# -*- coding: utf-8 -*-
"""Zero · Computer Use (captura de pantalla, mouse, teclado, apps) vía ctypes + PIL."""
from __future__ import annotations
import ctypes, subprocess, os, time
from pathlib import Path
from ctypes import wintypes

ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS = ROOT / "database" / "screenshots"


def screenshot(path=None):
    from PIL import ImageGrab
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    if path is None:
        path = SCREENSHOTS / f"screen_{int(time.time())}.png"
    path = Path(path)
    im = ImageGrab.grab()
    im.save(path)
    return {"ok": True, "path": str(path), "size": list(im.size)}


def _set_cursor(x, y):
    ctypes.windll.user32.SetCursorPos(int(x), int(y))


def move_mouse(x, y):
    _set_cursor(x, y)
    return {"ok": True}


def click(x, y, button="left", double=False):
    _set_cursor(x, y)
    time.sleep(0.05)
    if button == "left":
        down, up = 0x0002, 0x0004  # MOUSEEVENTF_LEFTDOWN/UP
    elif button == "right":
        down, up = 0x0008, 0x0010
    else:
        down, up = 0x0020, 0x0040
    ctypes.windll.user32.mouse_event(down, 0, 0, 0, 0)
    ctypes.windll.user32.mouse_event(up, 0, 0, 0, 0)
    if double:
        time.sleep(0.05)
        ctypes.windll.user32.mouse_event(down, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(up, 0, 0, 0, 0)
    return {"ok": True}


def type_text(text):
    # Usar WScript.Shell SendKeys vía PowerShell para soportar unicode
    escaped = text.replace("{", "{{").replace("}", "}}").replace("+", "{+}").replace("^", "{^}").replace("%", "{%}").replace("~", "{~}").replace("(", "{(}").replace(")", "{)}")
    ps = f'$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys("{escaped}")'
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], timeout=15, capture_output=True)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def press_key(key):
    # key: 'enter','tab','esc','ctrl+c', etc.
    mapping = {
        "enter": "{ENTER}", "tab": "{TAB}", "esc": "{ESC}", "backspace": "{BACKSPACE}",
        "delete": "{DELETE}", "up": "{UP}", "down": "{DOWN}", "left": "{LEFT}", "right": "{RIGHT}",
        "home": "{HOME}", "end": "{END}", "pageup": "{PGUP}", "pagedown": "{PGDN}",
    }
    k = key.lower()
    if k in mapping:
        code = mapping[k]
    elif k.startswith("ctrl+"):
        code = "^" + k[5:]
    elif k.startswith("alt+"):
        code = "%" + k[4:]
    elif k.startswith("shift+"):
        code = "+" + k[6:]
    else:
        code = key
    ps = f'$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys("{code}")'
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], timeout=15, capture_output=True)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def launch_app(target):
    try:
        os.startfile(target) if not target.startswith("http") else subprocess.Popen(["cmd", "/c", "start", "", target], shell=True)
        return {"ok": True}
    except Exception as e:
        try:
            subprocess.Popen(target, shell=True)
            return {"ok": True}
        except Exception as e2:
            return {"ok": False, "error": str(e2)}


def list_windows():
    EnumWindows = ctypes.windll.user32.EnumWindows
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    IsWindowVisible = ctypes.windll.user32.IsWindowVisible

    results = []
    def cb(hwnd, _):
        if IsWindowVisible(hwnd):
            length = GetWindowTextLength(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buf, length + 1)
                results.append({"hwnd": hwnd, "title": buf.value})
        return True
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    EnumWindows(WNDENUMPROC(cb), 0)
    return {"ok": True, "windows": results[:80]}


def active_window_title():
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
    return {"ok": True, "title": buf.value, "hwnd": hwnd}
