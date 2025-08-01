import os
import time
import signal
import threading
from datetime import datetime
from pathlib import Path

from recorder.screen_recorder import start_screen_recording, stop_screen_recording
from recorder.system_audio_recorder import start_system_audio_recording, stop_system_audio_recording
from recorder.action_logger import start_action_logging, stop_action_logging


running = True
cleaned_up = threading.Event()

def signal_handler(sig, frame):
    global running
    if not cleaned_up.is_set():
        print("\n[Session] Ctrl+C detected. Stopping recording...")
        running = False
    else:
        print("[Session] Already shutting down... please wait.")

signal.signal(signal.SIGINT, signal_handler)

def run_session():
    session_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    session_dir = Path("data") / f"session_{session_time}"
    session_dir.mkdir(parents=True, exist_ok=True)

    print(f"[Session] Starting Aethermind session at {session_dir}")

    # Paths
    video_path = session_dir / "screen.mp4"
    audio_path = session_dir / "audio.wav"
    actions_path = session_dir / "actions.jsonl"

    # Start components
    print("[Session] Recording screen...")
    start_screen_recording(video_path)  # region param is not needed unless implemented

    print("[Session] Recording system audio...")
    start_system_audio_recording(audio_path)

    print("[Session] Logging keyboard and mouse actions...")
    start_action_logging(actions_path)

    # Wait for Ctrl+C
    try:
        while running:
            time.sleep(1)
    finally:
        print("[Session] Cleaning up...")
        stop_screen_recording()
        stop_system_audio_recording()
        stop_action_logging()

        metadata = {
            "start_time": session_time,
            "video": str(video_path),
            "audio": str(audio_path),
            "actions": str(actions_path),
        }

        with open(session_dir / "session.json", "w") as f:
            import json
            json.dump(metadata, f, indent=2)

        print("[Session] Session ended and saved.")
        cleaned_up.set()

if __name__ == "__main__":
    run_session()