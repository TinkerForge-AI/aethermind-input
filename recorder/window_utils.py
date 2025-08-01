import subprocess
import re
import time
import os

# Print DISPLAY for debugging
print(f"[DEBUG] Python DISPLAY: {os.environ.get('DISPLAY')}")
print(subprocess.check_output(["wmctrl", "-lG"], text=True))

# ───────────────────────────────────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────────────────────────────────

_WMCTRL_RE = re.compile(r"""
    ^([0x0-9A-Fa-f]+)\s+      # window id (hex)
    \S+\s+\S+\s+              # desktop, pid/host (ignored)
    (\d+)\s+(\d+)\s+          # x   y
    (\d+)\s+(\d+)\s+          # w   h
    (.+)$                     # title (hostname + actual title)
""", re.VERBOSE)


def _wmctrl_list():
    """Return list of (win_id_hex, x, y, w, h, title)."""
    output = subprocess.check_output(["wmctrl", "-lG"], text=True)
    out = []
    for line in output.splitlines():
        print(f"[DEBUG] Parsing line: {line}")
        parts = line.split(None, 7)  # Split into at most 8 fields
        if len(parts) == 8:
            win_id, desktop, x, y, w, h, host, title = parts
            print(f"[DEBUG] Parsed fields: win_id={win_id}, x={x}, y={y}, w={w}, h={h}, title={title}")
            out.append((win_id, int(x), int(y), int(w), int(h), title.strip()))
        else:
            print(f"[DEBUG] Could not parse line: {line}")
    print(f"[DEBUG] _wmctrl_list returning: {len(out)} windows")
    return out


# ───────────────────────────────────────────────────────────────────────────────
# Public API
# ───────────────────────────────────────────────────────────────────────────────

def focus_window(window_name: str, retry: int = 5, wait: float = 0.2):
    """
    Bring the first window whose title *contains* `window_name` (case-insensitive)
    to the foreground using wmctrl. Retries a few times so the DE can react.
    """
    for attempt in range(retry):
        found = False
        titles = []
        print(f"[DEBUG] Attempt {attempt+1}/{retry}: Listing all window titles...")
        for win_id, *_ , title in _wmctrl_list():
            clean_title = title.strip()
            titles.append(clean_title)
            print(f"[DEBUG] Window: '{clean_title}' (len={len(clean_title)})")
            # Match if title ends with window_name (case-insensitive) to avoid Chrome tabs
            if clean_title.lower().endswith(window_name.lower()):
                print(f"[DEBUG] Found match ending with '{window_name}': '{clean_title}'")
                subprocess.call(["wmctrl", "-ia", win_id])  # activate
                time.sleep(wait)
                return
        print(f"[DEBUG] Window titles found: {titles}")
        time.sleep(wait)
    print(f"[DEBUG] No window titled exactly '{window_name}' found after {retry} attempts.")
    raise RuntimeError(f"No window titled exactly '{window_name}' found to focus.")


def get_window_region(window_name: str):
    """
    Return (x, y, w, h) for the FIRST window whose title contains `window_name`.
    Raises if not found.
    """
    print(f"[DEBUG] Searching for window region with title exactly '{window_name}'...")
    for _, x, y, w, h, title in _wmctrl_list():
        print(f"[DEBUG] Window: '{title.strip()}' (len={len(title.strip())})")
        # Match if title ends with window_name (case-insensitive) to avoid Chrome tabs
        if title.strip().lower().endswith(window_name.lower()):
            print(f"[DEBUG] Found match ending with '{window_name}' for region: '{title.strip()}'")
            return x, y, w, h
    print(f"[DEBUG] No window titled exactly '{window_name}' found for region.")
    raise RuntimeError(f"Window '{window_name}' not found.")


def focus_and_region(window_name: str, settle: float = 0.3):
    """Focus, then re-query geometry (some WMs move windows when focused)."""
    focus_window(window_name)
    time.sleep(settle)
    return get_window_region(window_name)


# Quick CLI test
if __name__ == "__main__":
    print(focus_and_region("Eastshade"))
