from shutil import which
from pathlib import Path
from dephell_pythons import Finder
from dephell_pythons._windows import WindowsFinder
from dephell_pythons._constants import IS_WINDOWS


def test_is_python():
    f = Finder()
    if not IS_WINDOWS:
        assert f.is_python(Path('tests', 'python3.7')) is True
    assert f.is_python(Path('tests', 'python3.5')) is False     # doesn't exist
    assert f.is_python(Path('tests', 'test_finder.py')) is False


def test_get_version():
    if IS_WINDOWS:
        return
    f = Finder()
    assert f.get_version(Path('tests', 'python3.7')) == '3.7.0'


def test_get_pythons_real():
    if IS_WINDOWS:
        f = WindowsFinder()
    else:
        f = Finder()
    assert len(f.pythons) > 0
    if not IS_WINDOWS:
        assert which('python').lower() in [str(p.path).lower() for p in f.pythons]
        assert which('python3').lower() in [str(p.path).lower() for p in f.pythons]


def test_get_pythons_fake():
    if IS_WINDOWS:
        return
    f = Finder()
    pythons = list(f.get_pythons([Path('tests')]))
    assert len(pythons) == 1
    assert pythons[0].name == 'python3.7'
