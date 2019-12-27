from shutil import which
from pathlib import Path

import pytest

from dephell_pythons import Finder
from dephell_pythons._windows import WindowsFinder
from dephell_pythons._constants import IS_WINDOWS


CONTENT = """
#!/usr/bin/env bash
if [[ $1 = '--version' ]]
then echo "Python 3.7.0"
else
  echo "3.7.0 (default, Dec 24 2018, 12:47:36) "
  echo "[GCC 5.4.0 20160609]"
fi
"""


@pytest.fixture
def fake_python(tmp_path: Path):
    path = tmp_path / 'python3.7'
    path.write_text(CONTENT.strip())
    path.chmod(0x777)
    return path


def test_is_python(fake_python: Path):
    f = Finder()
    if not IS_WINDOWS:
        assert f.is_python(fake_python) is True
    root = Path(__file__).parent
    assert f.is_python(root / 'python3.5') is False     # doesn't exist
    assert f.is_python(root / 'test_finder.py') is False


def test_get_version(fake_python: Path):
    if IS_WINDOWS:
        return
    f = Finder()
    assert f.get_version(fake_python) == '3.7.0'


def test_get_pythons_real():
    if IS_WINDOWS:
        f = WindowsFinder()
    else:
        f = Finder()
    assert len(f.pythons) > 0
    if not IS_WINDOWS:
        assert which('python').lower() in [str(p.path).lower() for p in f.pythons]
        assert which('python3').lower() in [str(p.path).lower() for p in f.pythons]


def test_get_pythons_fake(fake_python: Path):
    if IS_WINDOWS:
        return
    f = Finder()
    pythons = list(f.get_pythons([fake_python.parent]))
    assert len(pythons) == 1
    assert pythons[0].name == 'python3.7'
