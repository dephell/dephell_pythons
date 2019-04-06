import sys
from pathlib import Path
from dephell_pythons import Finder


def test_is_python():
    f = Finder()
    assert f.is_python(Path('tests', 'python3.7')) is True
    assert f.is_python(Path('tests', 'python3.5')) is False     # doesn't exist
    assert f.is_python(Path('tests', 'test_finder.py')) is False


def test_get_version():
    f = Finder()
    assert f.get_version(Path('tests', 'python3.7')) == '3.7.0'


def test_get_pythons_real():
    f = Finder()
    pythons = list(f.get_pythons())
    assert len(pythons) > 0
    assert sys.executable in map(str, pythons)


def test_get_pythons_fake():
    f = Finder()
    pythons = list(f.get_pythons([Path('tests')]))
    assert len(pythons) == 1
    assert pythons[0].name == 'python3.7'
