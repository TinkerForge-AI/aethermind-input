import subprocess
import threading
from pathlib import Path

_process = None

def start_system_audio_recording(output_path):
    '''
    Records system audio using PulseAudio monitor (Linux).
    You may need to determine the correct monitor source with:
    `pactl list short sources`
    '''
    global _process
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Auto-detect PulseAudio default monitor
    try:
        import subprocess
        result = subprocess.run(
            ["pactl", "list", "short", "sources"],
            stdout=subprocess.PIPE,
            text=True
        )
        monitor_line = next((line for line in result.stdout.splitlines() if ".monitor" in line), None)
        if monitor_line:
            monitor_name = monitor_line.split()[1]
        else:
            raise RuntimeError("No PulseAudio monitor source found.")
    except Exception as e:
        raise RuntimeError("Error detecting PulseAudio monitor source: " + str(e))

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "pulse",
        "-i", monitor_name,
        str(output_path)
    ]

    _process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def stop_system_audio_recording():
    global _process
    if _process:
        _process.terminate()
        _process.wait()
        _process = None