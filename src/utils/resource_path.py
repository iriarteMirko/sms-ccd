import sys
import os


def resource_path(relative_path: str) -> str:
    try:
        base_path: str = sys._MEIPASS
    except Exception:
        base_path: str = os.path.abspath(".")
    return os.path.join(base_path, relative_path)