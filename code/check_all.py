"""Run every offline check; stop at the first failure. Uses only Python's standard library."""

from pathlib import Path
import subprocess
import sys

CODE_DIR = Path(__file__).resolve().parent
COMMANDS = (
    ('construction_1104.py', '--check'),
    ('construction_5744.py', '--check'),
    ('verify.py',),
    ('verify_funsearch.py',),
    ('make_diagrams.py', '--check'),
    ('-m', 'unittest', 'discover', '-s', 'tests', '-v'),
)


def main():
    for command in COMMANDS:
        print('\nRunning:', ' '.join(command), flush=True)
        result = subprocess.run([sys.executable, *command], cwd=CODE_DIR)
        if result.returncode:
            return result.returncode
    print('\nPASS: all coordinate, cap, FunSearch, diagram, and unit checks.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
