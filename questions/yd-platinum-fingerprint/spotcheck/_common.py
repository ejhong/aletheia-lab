# Shared helper for the spot-check scripts: loads analysis/pt_fingerprint.py as a module. Not run on its own.
import importlib.util
import pathlib

QDIR = pathlib.Path(__file__).resolve().parent.parent


def load_program():
    spec = importlib.util.spec_from_file_location("pt_fingerprint", QDIR / "analysis" / "pt_fingerprint.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
