import sys
from dephell_pythons import Pythons


def test_lib_paths():
    p = Pythons().current
    assert len(p.lib_paths) > 2
    # appveyor makes some hacks for python path
    libs_found = {path for path in sys.path if 'Scripts' not in path and 'dephell' not in path}
    libs_real = {str(path) for path in p.lib_paths if 'Scripts' not in str(path) and 'dephell' not in str(path)}
    assert libs_found == libs_real


def test_lib_path():
    p = Pythons().current
    assert 'site-packages' in str(p.lib_path)
