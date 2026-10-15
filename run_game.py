"""Launcher for BLOCK-GAME. Run this file from VS Code."""
from pathlib import Path
import os
import runpy

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
runpy.run_path(str(ROOT / "test.py"), run_name="__main__")
