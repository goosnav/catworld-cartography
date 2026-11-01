"""Compatibility entry point; R5 diagrams are generated together."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("make_epoch_figures.py")),run_name="__main__")
