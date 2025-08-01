
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
    """Signal handler for graceful shutdown on Ctrl+C."""
    global running
    if not cleaned_up.is_set():
        print("\n[Session] Ctrl+C detected. Stopping recording...")
        running = False
    else:
        print("[Session] Already shutting down... please wait.")

signal.signal(signal.SIGINT, signal_handler)

def run_session():
    """
    Run a synchronized capture session for screen, audio, and user actions.
    Handles graceful startup, shutdown, and metadata logging.
    """
    session_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    session_dir = Path("data") / f"session_{session_time}"
    session_dir.mkdir(parents=True, exist_ok=True)

    print(f"[Session] Starting Aethermind session at {session_dir}")

    # Paths
    video_path = session_dir / "screen.mp4"
    audio_path = session_dir / "audio.wav"
    actions_path = session_dir / "actions.jsonl"

    try:
        print("[Session] Recording screen...")
        try:
            start_screen_recording(video_path)
        except Exception as e:
            print(f"[Error] Failed to start screen recording: {e}")
            raise

        print("[Session] Recording system audio...")
        try:
            start_system_audio_recording(audio_path)
        except Exception as e:
            print(f"[Error] Failed to start system audio recording: {e}")
            try:
                stop_screen_recording()
            except Exception as e2:
                print(f"[Error] Failed to stop screen recording after audio error: {e2}")
            raise

        print("[Session] Logging keyboard and mouse actions...")
        try:
            start_action_logging(actions_path)
        except Exception as e:
            print(f"[Error] Failed to start action logging: {e}")
            try:
                stop_screen_recording()
            except Exception as e2:
                print(f"[Error] Failed to stop screen recording after action logger error: {e2}")
            try:
                stop_system_audio_recording()
            except Exception as e2:
                print(f"[Error] Failed to stop system audio recording after action logger error: {e2}")
            raise

        # Wait for Ctrl+C
        try:
            while running:
                time.sleep(1)
        finally:
            print("[Session] Cleaning up...")
            # Stop all components, log errors if any
            try:
                stop_screen_recording()
            except Exception as e:
                print(f"[Error] Failed to stop screen recording: {e}")
            try:
                stop_system_audio_recording()
            except Exception as e:
                print(f"[Error] Failed to stop system audio recording: {e}")
            try:
                stop_action_logging()
            except Exception as e:
                print(f"[Error] Failed to stop action logging: {e}")

            # Write session metadata
            metadata = {
                "start_time": session_time,
                "end_time": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                "video": str(video_path),
                "audio": str(audio_path),
                "actions": str(actions_path),
            }
            try:
                with open(session_dir / "session.json", "w") as f:
                    import json
                    json.dump(metadata, f, indent=2)
            except Exception as e:
                print(f"[Error] Failed to write session metadata: {e}")

            print("[Session] Session ended and saved.")
            cleaned_up.set()
    except Exception as e:
        print(f"[Session] Fatal error: {e}")
        cleaned_up.set()

if __name__ == "__main__":
    run_session()