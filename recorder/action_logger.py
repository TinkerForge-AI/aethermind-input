import time
import json
import threading
from pynput import keyboard, mouse
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener, Button

# Shared state
keyboard_state = set()
mouse_position = (0, 0)
mouse_buttons = {"left": False, "right": False, "middle": False}
mouse_scroll = [0, 0]
running = True

# Track mouse button presses
mouse_buttons_pressed = set()

def on_key_press(key):
    try:
        keyboard_state.add(key.char)
    except AttributeError:
        keyboard_state.add(str(key))

def on_key_release(key):
    try:
        keyboard_state.discard(key.char)
    except AttributeError:
        keyboard_state.discard(str(key))

def on_click(x, y, button, pressed):
    name = str(button).split('.')[-1]  # 'left', 'right', 'middle'
    if pressed:
        mouse_buttons_pressed.add(name)
    else:
        mouse_buttons_pressed.discard(name)

    # Update shared state based on active pressed buttons
    mouse_buttons["left"] = "left" in mouse_buttons_pressed
    mouse_buttons["right"] = "right" in mouse_buttons_pressed
    mouse_buttons["middle"] = "middle" in mouse_buttons_pressed

def on_move(x, y):
    global mouse_position
    mouse_position = (x, y)

def on_scroll(x, y, dx, dy):
    global mouse_scroll
    mouse_scroll = [dx, dy]

def log_actions(log_path="actions.jsonl", interval=0.1):
    with open(log_path, "w") as f:
        while running:
            timestamp = time.time()
            entry = {
                "time": timestamp,
                "keys": sorted(list(keyboard_state)),
                "mouse": {
                    "position": list(mouse_position),
                    "buttons": dict(mouse_buttons),
                    "scroll": list(mouse_scroll),
                },
            }
            f.write(json.dumps(entry) + "\n")
            f.flush()

            # Reset scroll deltas
            mouse_scroll[0] = 0
            mouse_scroll[1] = 0

            time.sleep(interval)

logger_thread = None

def start_action_logging(log_path="actions.jsonl", interval=0.1):
    """
    Start logging keyboard and mouse actions to a file in a background thread.
    Returns the keyboard listener, mouse listener, and logger thread.
    """
    global running, logger_thread, keyboard_listener, mouse_listener
    running = True

    # Listeners
    keyboard_listener = KeyboardListener(on_press=on_key_press, on_release=on_key_release)
    mouse_listener = MouseListener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)

    keyboard_listener.start()
    mouse_listener.start()

    logger_thread = threading.Thread(target=log_actions, args=(log_path, interval))
    logger_thread.start()

    return keyboard_listener, mouse_listener, logger_thread

def stop_action_logging():
    """
    Stop the action logger thread and listeners, and wait for cleanup.
    """
    global running, logger_thread, keyboard_listener, mouse_listener
    if keyboard_listener:
        keyboard_listener.stop()
        keyboard_listener = None
    if mouse_listener:
        mouse_listener.stop()
        mouse_listener = None
    running = False
    if logger_thread is not None:
        logger_thread.join()
        logger_thread = None
