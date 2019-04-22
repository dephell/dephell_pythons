import os
import subprocess
from fnmatch import fnmatch
from functools import lru_cache
from operator import attrgetter
from packaging.version import Version
from pathlib import Path
from typing import Optional, List, Iterable, Iterator

import attr

from ._cached_property import cached_property
from ._constants import PYTHON_IMPLEMENTATIONS, SUFFIX_PATTERNS
from ._python import Python


@attr.s(frozen=True, hash=True)
class Finder:

    # properties

    @cached_property
    def shims(self) -> List[Path]:
        known_paths = (
            # pyenv
            '~/.pyenv',
            '/opt/pyenv',
            os.environ.get('PYENV_ROOT'),
            # asdf
            '~/.asdf',
            os.environ.get('ASDF_DATA_DIR'),
        )
        paths = []
        for path in known_paths:  # type: Path # type: ignore
            if not path:
                continue
            path = os.path.expandvars(path).strip('"')  # type: ignore
            path = Path(path).expanduser()
            if path.exists():
                paths.append(path.resolve())
        return paths

    @cached_property
    def paths(self) -> List[Path]:
        all_paths = os.environ.get('PATH', '').split(os.pathsep)
        good_paths = []  # type: List[Path]
        for path in all_paths:  # type: Path # type: ignore
            path = os.path.expandvars(path.strip('"'))  # type: ignore
            path = Path(path).expanduser()
            if not path.exists():
                continue
            path = path.resolve()
            if self.in_shims(path):
                continue
            good_paths.append(path)

        for shim in self.shims:
            path = shim / 'versions'
            if path.exists():
                good_paths.append(path)

        return good_paths

    @cached_property
    def pythons(self) -> List[Python]:
        pythons = []
        for path in self.get_pythons():
            pythons.append(Python(
                path=path,
                version=Version(self.get_version(path)),
                implementation=self.get_implementation(path) or 'python',
                shim=self.in_shims(path=path),
            ))
        pythons.sort(key=attrgetter('version'), reverse=True)
        return pythons

    # public methods

    def in_shims(self, path: Path) -> bool:
        for shim in self.shims:
            if str(path).startswith(str(shim)):
                return True
        return False

    @lru_cache(maxsize=32)
    def get_version(self, path: Path) -> str:
        # get version from CLI for cpython
        if path.name.startswith('python'):
            # this works much faster, so let's do it if possible
            result = subprocess.run([str(path), '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                raise LookupError(result.stderr.decode())
            # cpython 2 writes version into stderr
            output = result.stdout.decode() + ' ' + result.stderr.decode()
            return output.split()[1].rstrip('+')

        # get version from interpreter for other implementations (like pypy)
        command = r'print(__import__("sys").version)'
        result = subprocess.run([str(path), '-c', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise LookupError(result.stderr.decode())
        return result.stdout.decode().split()[0].rstrip('+')

    @staticmethod
    def get_implementation(path: Path) -> Optional[str]:
        for implementation in PYTHON_IMPLEMENTATIONS:
            if path.name.startswith(implementation):
                return implementation
        return None

    def is_python(self, path: Path) -> bool:
        # https://stackoverflow.com/a/377028/8704691
        try:
            if not path.is_file():
                return False
        except PermissionError:
            return False
        if not os.access(str(path), os.X_OK):
            return False

        implementation = self.get_implementation(path=path)
        if implementation is None:
            return False

        if path.suffix in {'.exe', '.py', '.fish', '.sh'}:
            path = path.with_suffix('')
        suffix = path.name[len(implementation):]
        if not suffix:
            return True
        for pattern in SUFFIX_PATTERNS:
            if fnmatch(name=suffix, pat=pattern):
                return True
        return False

    def get_pythons(self, paths: Iterable[Path] = None) -> Iterator[Path]:
        if paths is None:
            paths = self.paths
        for path in paths:
            # single binary
            if path.is_file():
                if self.is_python(path=path):
                    yield path
                continue

            # directory with executables
            for executable in path.iterdir():
                if self.is_python(path=executable):
                    yield executable

            # shims directory
            for executable in path.glob('*/bin/*'):
                if self.is_python(path=executable):
                    yield executable
