from pynput import keyboard
#!/usr/bin/env python3
import time
import signal
import argparse
from datetime import datetime
from pathlib import Path

from recorder.screen_recorder import start_screen_recording, stop_screen_recording
from recorder.system_audio_recorder import start_system_audio_recording, stop_system_audio_recording
from recorder.action_logger import start_action_logging, stop_action_logging
from recorder.window_utils import focus_and_region

running = True

# Track Alt+Tab state for ending training session
alt_pressed = False
tab_pressed = False

def on_press(key):
    global running, alt_pressed, tab_pressed
    try:
        if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
            alt_pressed = True
        if key == keyboard.Key.tab:
            tab_pressed = True
        if alt_pressed and tab_pressed:
            print("\n[Session] Alt+Tab detected. Stopping early...")
            running = False
    except Exception:
        pass

def on_release(key):
    global alt_pressed, tab_pressed
    if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
        alt_pressed = False
    if key == keyboard.Key.tab:
        tab_pressed = False

def signal_handler(sig, frame):
    global running
    print("\n[Session] Ctrl+C detected. Stopping early...")
    running = False

signal.signal(signal.SIGINT, signal_handler)

def run_session(duration, window_name, output_base="data"):
    # Start keyboard listener for Alt+Tab
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    session_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    session_dir = Path(output_base) / f"session_{session_time}"
    session_dir.mkdir(parents=True, exist_ok=True)

    print(f"[Session] Focusing '{window_name}' window…")
    region = focus_and_region(window_name)
    print(f"[Session] Capturing region: {region}")

    video_path = session_dir / "screen.mp4"
    audio_path = session_dir / "audio.wav"
    actions_path = session_dir / "actions.jsonl"

    start_screen_recording(video_path, region=region)
    start_system_audio_recording(audio_path)
    start_action_logging(actions_path)

    start = time.time()
    try:
        while running and (time.time() - start) < duration:
            time.sleep(0.5)
    finally:
        listener.stop()
        print("[Session] Stopping capture...")
        stop_screen_recording()
        stop_system_audio_recording()
        stop_action_logging()

        metadata = {
            "start_time": session_time,
            "duration_requested": duration,
            "actual_duration": round(time.time() - start, 2),
            "video": str(video_path),
            "audio": str(audio_path),
            "actions": str(actions_path),
        }
        with open(session_dir / "session.json", "w") as f:
            import json
            json.dump(metadata, f, indent=2)

        print(f"[Session] Completed. Session saved at {session_dir}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-d", "--duration", type=int, default=300, help="Capture duration in seconds (default 300)")
    p.add_argument("-w", "--window", type=str, default="Eastshade", help="Window title to capture")
    p.add_argument("-o", "--output", type=str, default="data", help="Base output directory")
    args = p.parse_args()
    run_session(args.duration, args.window, args.output)
