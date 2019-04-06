# built-in
import subprocess
from pathlib import Path
from typing import List

# external
import attr
from packaging.version import Version

from ._cached_property import cached_property


@attr.s()
class Python:
    path = attr.ib(type=Path)
    version = attr.ib(type=Version)
    implementation = attr.ib(type=str)
    abstract = attr.ib(type=bool, default=False)

    def get_short_version(self, size=2) -> Version:
        numbers = map(str, self.version.release[:size])
        return Version('.'.join(numbers))

    @property
    def name(self):
        return self.path.name

    @cached_property
    def lib_paths(self) -> List[Path]:
        command = r'print("\n".join(__import__("sys").path))'
        result = subprocess.run([str(self.path), '-c', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise LookupError(result.stderr.decode())
        paths = [path.strip() for path in result.stdout.decode().split('\n')]
        return [Path(path) for path in paths if path]

    @property
    def lib_path(self) -> Path:
        for path in self.lib_paths:
            if 'site-packages' in path.parts:
                return path
        for path in self.lib_paths:
            if 'Lib' in path.parts:
                return path
        raise LookupError('cannot find lib path')
