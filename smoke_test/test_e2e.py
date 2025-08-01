import json
import math
import shutil
import subprocess
import sys
from pathlib import Path


def test_e2e():
    root = Path(__file__).resolve().parents[2]
    input_repo = root / 'aethermind-input'
    perception_repo = root / 'aethermind-perception'

    assert input_repo.exists(), 'input repo missing'
    assert perception_repo.exists(), 'perception repo missing'

    session = 'session_test'
    session_dir = input_repo / 'data' / session
    if session_dir.exists():
        shutil.rmtree(session_dir)
    session_dir.mkdir(parents=True)

    fixture_dir = input_repo / 'fixtures'
    fixture_dir.mkdir(exist_ok=True)
    for name in ['test.mp4', 'test.wav']:
        (fixture_dir / name).write_text('dummy')
        shutil.copy(fixture_dir / name, session_dir / name)
    (session_dir / 'actions.jsonl').write_text('{"timestamp":0,"action":"noop"}\n')

    output_root = perception_repo / 'sessions' / session
    if output_root.exists():
        shutil.rmtree(output_root)

    subprocess.check_call([sys.executable, str(perception_repo / 'session_runner.py'), str(session_dir), str(output_root)])

    session_json = json.loads((output_root / 'session.json').read_text())
    expected = math.ceil(session_json['clip_length'] / session_json['chunk_duration'])
    clips = list((output_root / 'clips').glob('*'))
    assert len(clips) == expected
