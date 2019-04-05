import sys
from dephell_pythons import Pythons


def test_lib_paths():
    p = Pythons().current
    assert len(p.lib_paths) > 2
    assert set(map(str, p.lib_paths)) == set(sys.path)


def test_lib_path():
    p = Pythons().current
    assert 'site-packages' in str(p.lib_path)
