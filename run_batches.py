import csv
import shlex
import subprocess
import sys
from pathlib import Path


def find_framepack_dir() -> Path:
    """Locate the framepack repository directory.

    The operator repository usually lives alongside the actual framepack
    repository.  ``framepackoperator`` also matches the ``framepack*`` pattern
    so we need to ignore our own directory when searching.
    """

    repo_root = Path(__file__).resolve().parent
    parent = repo_root.parent

    candidates = [
        p
        for p in parent.iterdir()
        if p.is_dir()
        and p.name.startswith("framepack")
        and p != repo_root
    ]

    if not candidates:
        raise FileNotFoundError("framepack directory not found")

    # Prefer a directory named exactly 'framepack' if present for stability
    for c in candidates:
        if c.name == "framepack":
            return c

    return sorted(candidates)[0]


def run_batch(framepack_dir: Path, cmd_args: str, work_dir: Path):
    script_path = framepack_dir / 'webui' / 'oneframe_ichi.py'
    cmd = [sys.executable, str(script_path)] + shlex.split(cmd_args)
    subprocess.run(cmd, cwd=framepack_dir, check=True)


def main():
    repo_root = Path(__file__).resolve().parent
    framepack_dir = find_framepack_dir()

    video_root = repo_root / 'videos'
    video_root.mkdir(exist_ok=True)

    input_csv = repo_root / 'input.csv'
    output_records = []

    with open(input_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            batch = row['batch_name']
            args = row.get('args', '')
            batch_dir = video_root / batch
            batch_dir.mkdir(parents=True, exist_ok=True)
            run_batch(framepack_dir, args, batch_dir)
            output_records.append({'batch_name': batch, 'output_dir': str(batch_dir)})

    with open(repo_root / 'outputs.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['batch_name', 'output_dir'])
        writer.writeheader()
        writer.writerows(output_records)


if __name__ == '__main__':
    main()
