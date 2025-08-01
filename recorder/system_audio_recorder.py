import os
import subprocess
import signal
from pathlib import Path

_process = None

def start_system_audio_recording(output_path):
    """
    Records system audio using PulseAudio monitor (Linux).
    """
    global _process
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Detect default PulseAudio sink monitor
    try:
        info = subprocess.run(
            ["pactl", "info"], stdout=subprocess.PIPE, text=True
        ).stdout
        sink_line = next(
            (l for l in info.splitlines() if l.lower().startswith("default sink:")), None
        )
        if not sink_line:
            raise RuntimeError("Could not determine default PulseAudio sink.")
        sink_name = sink_line.split(":", 1)[1].strip()
        monitor_name = os.environ.get("AETHERMIND_MONITOR", f"{sink_name}.monitor")
        print(f"[Audio] Using PulseAudio monitor: {monitor_name}")
    except Exception as e:
        raise RuntimeError("Error detecting PulseAudio monitor: " + str(e))

    cmd = [
        "ffmpeg",
        "-f", "pulse",
        "-i", monitor_name,
        "-acodec", "pcm_s16le",
        "-ar", "44100",
        "-ac", "2",
        "-y", str(output_path)
    ]
    print(f"[Audio] Running ffmpeg command: {' '.join(cmd)}")
    _process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def stop_system_audio_recording():
    """
    Stops the system audio recording.
    """
    global _process
    if _process:
        _process.send_signal(signal.SIGINT)
        _process.wait()
        _process = None