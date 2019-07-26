# built-in
import os
from pathlib import Path


# https://stackoverflow.com/a/377028/8704691
def is_executable(path: Path) -> bool:
    """
    1. It exists
    2. It's a file
    3. We can execute it
    """
    try:
        if not path.is_file():
            return False
    except PermissionError:
        return False
    if not os.access(str(path), os.X_OK):
        return False
    return True


def is_dir(path: Path) -> bool:
    """
    1. It exists
    2. It's a dir
    3. We can read it
    """
    try:
        if not path.is_dir():
            return False
    except PermissionError:
        return False
    if not os.access(str(path), os.R_OK):
        return False
    return True
