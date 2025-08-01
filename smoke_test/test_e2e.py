import json
import math
import shutil
import subprocess
import sys
from pathlib import Path


# Command to run from root folder: 
#
# source .venv/bin/activate
# pytest -s smoke_test/test_e2e.py 

def test_e2e():
    print("Starting e2e smoke test...")
    root = Path(__file__).resolve().parents[2]
    input_repo = root / 'aethermind-input'
    perception_repo = root / 'aethermind-perception'

    print(f"Checking input repo at {input_repo}")
    assert input_repo.exists(), 'input repo missing'
    print(f"Checking perception repo at {perception_repo}")
    assert perception_repo.exists(), 'perception repo missing'

    session = 'session_test'
    session_dir = input_repo / 'data' / session
    if session_dir.exists():
        print(f"Removing old session dir {session_dir}")
        shutil.rmtree(session_dir)
    session_dir.mkdir(parents=True)
    print(f"Created session dir {session_dir}")

    fixture_dir = input_repo / 'fixtures'
    fixture_dir.mkdir(exist_ok=True)
    # Only copy, never overwrite or write to the fixture files
    for name in ['test.mp4', 'test.wav']:
        src = fixture_dir / name
        dst = session_dir / name
        if not src.exists():
            raise FileNotFoundError(f"Missing fixture file: {src}")
        shutil.copy(src, dst)
    (session_dir / 'actions.jsonl').write_text('{"timestamp":0,"action":"noop"}\n')
    print("Copied fixtures and created actions.jsonl")

    output_root = perception_repo / 'sessions'
    # Remove all old output dirs for a clean test
    if output_root.exists():
        for d in output_root.iterdir():
            if d.is_dir():
                shutil.rmtree(d)

    print(f"Running perception session_runner.py...")
    subprocess.check_call([
        sys.executable,
        str(perception_repo / 'session_runner.py'),
        '--video', str(session_dir / 'test.mp4'),
        '--audio', str(session_dir / 'test.wav'),
    ], cwd=str(perception_repo))
    print("session_runner.py completed")

    # Find the newest output directory
    output_dirs = [d for d in output_root.iterdir() if d.is_dir()]
    if not output_dirs:
        raise FileNotFoundError("No output session directory found in perception_repo/sessions/")
    latest_output = max(output_dirs, key=lambda d: d.stat().st_mtime)

    print(f"Using output directory: {latest_output}")

    session_json = json.loads((latest_output / 'session.json').read_text())
    expected = len(session_json['chunks'])
    # Count chunk video files directly in the session output directory
    clips = [f for f in latest_output.iterdir() if f.is_file() and f.name.startswith('chunk_') and f.suffix == '.mp4']
    print(f"Expected {expected} clips, found {len(clips)}")
    assert len(clips) == expected
    print("PASS: e2e smoke test succeeded")
