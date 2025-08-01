## Aethermind Input Capture Module

This module coordinates the synchronized capture of screen video (`.mp4`), system audio (`.wav`), and keyboard/mouse actions (`.jsonl`) for training data preparation.

### Usage

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   sudo apt install ffmpeg  # Linux only, for screen/audio capture
   ```

2. **Run the capture session:**
   ```bash
   python capture_session.py
   ```

3. **Stop the session:**
   Press `Ctrl+C` once in the terminal. All files will be finalized and saved in a new `data/session_YYYY-MM-DD_HH-MM-SS/` directory.

### Output

- `screen.mp4` — Screen recording
- `audio.wav` — System audio recording
- `actions.jsonl` — Keyboard/mouse actions
- `session.json` — Metadata (start/end time, file paths)

### Notes

- Ensure `ffmpeg` is installed and available in your system PATH.
- All resources are cleaned up on exit. If the terminal becomes unresponsive, type `reset` and press Enter.

### Troubleshooting

- If you see errors about missing `ffmpeg`, install it with your system package manager.
- If files are not finalized, ensure you only need to press `Ctrl+C` once and wait for the session to end.

---
For further development or integration, see the code docstrings and comments.# aethermind-input
The input coordination for Aethermind
