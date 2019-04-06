import os
import subprocess
from fnmatch import fnmatch
from functools import lru_cache
from operator import attrgetter
from packaging.version import Version
from pathlib import Path
from typing import Optional, List, Iterable, Iterator

from ._cached_property import cached_property
from ._constants import PYTHON_IMPLEMENTATIONS, SUFFIX_PATTERNS
from ._python import Python


class Finder:

    # properties

    @cached_property
    def pyenv_path(self) -> Optional[Path]:
        if not {'PYENV_SHELL', 'PYENV_ROOT'} & set(os.environ):
            return None
        path = os.environ.get('PYENV_ROOT', '~/.pyenv')
        path = os.path.expandvars(path).strip('"')
        try:
            return Path(path).expanduser().resolve()
        except FileNotFoundError:
            return None

    @cached_property
    def asdf_path(self) -> Optional[Path]:
        if not {'ASDF_DIR', 'ASDF_DATA_DIR'} & set(os.environ):
            return None
        path = os.environ.get('ASDF_DATA_DIR', '~/.asdf')
        path = os.path.expandvars(path).strip('"')
        try:
            return Path(path).expanduser().resolve()
        except FileNotFoundError:
            return None

    @cached_property
    def shims(self) -> List[Path]:
        paths = []
        if self.pyenv_path is not None:
            paths.append(self.pyenv_path)
        if self.asdf_path is not None:
            paths.append(self.asdf_path)
        return paths

    @cached_property
    def paths(self) -> List[Path]:
        all_paths = os.environ.get('PATH', '').split(os.pathsep)
        good_paths = []
        for path in all_paths:
            path = os.path.expandvars(path.strip('"'))
            path = Path(path).expanduser()
            if not path.exists():
                continue
            path = path.resolve()
            if not self.in_shims(path):
                good_paths.append(path)
        return good_paths

    @cached_property
    def pythons(self) -> List[Python]:
        pythons = []
        for path in self.get_pythons():
            pythons.append(Python(
                path=path,
                version=Version(self.get_version(path)),
                implementation=self.get_implementation(path),
            ))
        pythons.sort(key=attrgetter('version'), reverse=True)
        return pythons

    # public methods

    def in_shims(self, path: Path) -> bool:
        for shim in self.shims:
            if str(path).startswith(str(shim)):
                return True
        return False

    @staticmethod
    @lru_cache(maxsize=32)
    def get_version(path: Path) -> str:
        if path.name.startswith('python'):
            # this works much faster, so let's do it if possible
            result = subprocess.run([str(path), '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                raise LookupError(result.stderr.decode())
            # cpython 2 writes version into stderr
            output = result.stdout.decode() + ' ' + result.stderr.decode()
            return output.split()[1]

        command = r'print(__import__("sys").version)'
        result = subprocess.run([str(path), '-c', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise LookupError(result.stderr.decode())
        return result.stdout.decode().split()[0]

    @staticmethod
    def get_implementation(path: Path) -> Optional[str]:
        for implementation in PYTHON_IMPLEMENTATIONS:
            if path.name.startswith(implementation):
                return implementation
        return None

    def is_python(self, path: Path) -> bool:
        # https://stackoverflow.com/a/377028/8704691
        if not path.is_file():
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
            if path.is_file():
                if self.is_python(path=path):
                    yield path
                continue
            for executable in path.iterdir():
                if self.is_python(path=executable):
                    yield executable
