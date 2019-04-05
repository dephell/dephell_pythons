# external
import pytest
from packaging.version import Version

# project
from dephell_pythons import Pythons


@pytest.mark.parametrize('version', [
    '2.7',
    '3.0',
    '3.4',
    '3.5',
    '3.6',
    '3.7',
])
def test_get_by_version(version):
    manager = Pythons(abstract=True)
    python = manager.get_by_version(Version(version))
    assert str(python.version).startswith(version)
