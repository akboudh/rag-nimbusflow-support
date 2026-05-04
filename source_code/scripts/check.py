from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> int:
    print("+ " + " ".join(command))
    completed = subprocess.run(command, cwd=ROOT)
    return completed.returncode


def main() -> int:
    checks = [
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        [sys.executable, "scripts/evaluate.py"],
    ]
    for command in checks:
        status = run(command)
        if status:
            return status
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
