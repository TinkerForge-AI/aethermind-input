import subprocess
import signal

ffmpeg_process = None

def start_screen_recording(output_path="screen.mp4", fps=30, region=None):
    global ffmpeg_process
    ffmpeg_command = [
        "ffmpeg",
        "-video_size", "1920x1080",  # or detect via pyautogui.size()
        "-framerate", str(fps),
        "-f", "x11grab",             # or "gdigrab" on Windows, or "avfoundation" on macOS
        "-i", ":0.0",                # X11 display (Linux) — update based on OS
        "-y", str(output_path)
    ]
    ffmpeg_process = subprocess.Popen(ffmpeg_command)

def stop_screen_recording():
    global ffmpeg_process
    if ffmpeg_process:
        ffmpeg_process.send_signal(signal.SIGINT)
        ffmpeg_process.wait()
        ffmpeg_process = None