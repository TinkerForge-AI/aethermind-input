import subprocess
import signal

ffmpeg_process = None

def get_screen_size():
    """Return (width, height) of the full X screen using xrandr, or fallback to 3840x1080."""
    try:
        output = subprocess.check_output(['xrandr'], text=True)
        import re
        m = re.search(r'current (\d+) x (\d+)', output)
        if m:
            return int(m.group(1)), int(m.group(2))
    except Exception as e:
        print(f"[WARNING] Could not determine screen size dynamically: {e}")
    return 3840, 1080  # fallback default

def start_screen_recording(output_path="screen.mp4", fps=30, region=None):
    """
    Start screen recording using ffmpeg, targeting a specific window region if provided.
    region: (x, y, w, h) tuple. If None, defaults to full HD at (0,0).
    Shows ffmpeg output for debugging.
    """
    global ffmpeg_process
    if region is not None:
        x, y, w, h = map(int, region)
        max_width, max_height = get_screen_size()
        
        # Adjust capture area if it exceeds screen bounds
        if x + w > max_width:
            w = max_width - x
            print(f"[WARNING] Adjusted width to {w} to fit within screen bounds")
        if y + h > max_height:
            h = max_height - y
            print(f"[WARNING] Adjusted height to {h} to fit within screen bounds")
        if x < 0:
            x = 0
            print(f"[WARNING] Adjusted x to {x} to fit within screen bounds")
        if y < 0:
            y = 0
            print(f"[WARNING] Adjusted y to {y} to fit within screen bounds")
            
        video_size = f"{w}x{h}"
        input_str = f":0.0+{x},{y}"
    else:
        video_size = "1920x1080"
        input_str = ":0.0"
    ffmpeg_command = [
        "ffmpeg",
        "-video_size", video_size,
        "-framerate", str(fps),
        "-f", "x11grab",
        "-i", input_str,
        "-y", str(output_path)
    ]
    print(f"[DEBUG] Running ffmpeg command: {' '.join(ffmpeg_command)}")
    ffmpeg_process = subprocess.Popen(ffmpeg_command)  # Show ffmpeg output for debugging

def stop_screen_recording():
    global ffmpeg_process
    if ffmpeg_process:
        ffmpeg_process.send_signal(signal.SIGINT)
        ffmpeg_process.wait()
        ffmpeg_process = None

# Manual audio troubleshooting steps:
# 1. Run 'pactl list short sources' in your terminal and look for a line ending with '.monitor'.
# 2. Use 'pavucontrol' (install if needed) to ensure the correct monitor is capturing the game audio.
# 3. Test your ffmpeg audio command manually, e.g.:
#    ffmpeg -f pulse -i <monitor_name> test.wav
# 4. Play back test.wav to confirm you hear the game audio.