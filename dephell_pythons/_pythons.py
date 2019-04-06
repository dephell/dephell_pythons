# built-in
import os
import sys
from operator import attrgetter
from pathlib import Path
from platform import python_implementation, python_version
from typing import Iterator, Optional, Union, List

# external
import attr
from packaging.version import InvalidVersion, Version
from pythonfinder import WindowsFinder

# project
from dephell_specifier import RangeSpecifier

# app
from ._cached_property import cached_property
from ._constants import PYTHONS
from ._finder import Finder
from ._python import Python


def _get_finder():
    if os.name == "nt":
        return WindowsFinder()
    return Finder()


@attr.s()
class Pythons:
    abstract = attr.ib(type=bool, default=False)
    finder = attr.ib(factory=_get_finder, repr=False)

    # PROPERTIES

    @property
    def current(self):
        return Python(
            path=Path(sys.executable),
            version=Version(python_version()),
            implementation=python_implementation(),
        )

    # PUBLIC METHODS

    def get_best(self, prefer: Union[None, Path, Version, RangeSpecifier] = None) -> Python:
        # no preferentions
        if not prefer:
            return self.current

        # given version
        if isinstance(prefer, Version):
            python = self.get_by_version(prefer)
            if python is None:
                msg = 'cannot find interpreter for given python version: '
                raise FileNotFoundError(msg + str(prefer))
            return python

        # given path
        if isinstance(prefer, Path):
            python = self.get_by_path(prefer)
            if python is None:
                msg = 'cannot find binary by given path: '
                raise FileNotFoundError(msg + str(prefer))
            return python

        # given constraint
        if isinstance(prefer, RangeSpecifier):
            python = self.get_by_spec(prefer)
            if python is None:
                msg = 'cannot find interpreter for given constraint: '
                raise FileNotFoundError(msg + str(prefer))
            return python

        if not isinstance(prefer, str):
            raise TypeError('invalid python preferention type: ' + str(type(prefer)))

        # looks like a path
        path = Path(prefer)
        if os.path.sep in prefer and not path.exists():
            msg = 'cannot find binary by given path: '
            raise FileNotFoundError(msg + str(prefer))
        if path.exists():
            python = self.get_by_path(path)
            if python is not None:
                return python

        # looks like constraint
        if set(prefer) & {'<', '>', '='}:
            python = self.get_by_spec(RangeSpecifier(prefer))
            if python is not None:
                return python

        # ok, let's try it like a version
        try:
            version = Version(prefer)
        except InvalidVersion:
            pass
        else:
            python = self.get_by_version(version)
            if python is not None:
                return python

        # ok, let's try it like a name
        python = self.get_by_name(prefer)
        if python is not None:
            return python

        # no success
        raise FileNotFoundError('cannot find interpretor: ' + str(prefer))

    def get_by_spec(self, specifier: RangeSpecifier) -> Python:
        for python in self:
            if python.version in specifier:
                return python
        for python in self:
            if python.get_short_version(size=3) in specifier:
                return python
        for python in self:
            if python.get_short_version(size=2) in specifier:
                return python
        return self.current

    def get_by_version(self, version: Version) -> Optional[Python]:
        # exact version (3.7.1 -> 3.7.1)
        for python in self:
            if python.version == version:
                return python

        # base version (3.7 -> 3.7.1)
        for base_version in (version.release[:3], version.release[:2]):
            for python in self:
                if python.version.release[:2] == base_version:
                    return python
        return None

    def get_by_name(self, name: str) -> Optional[Python]:
        for python in self:
            if python.name == name:
                return python
        return None

    def get_by_path(self, path: Path) -> Optional[Python]:
        if not path.exists():
            return None
        for python in self:
            if path.samefile(python.path):
                return python
        return None

    # PRIVATE METHODS

    def _get_from_pythonfinder(self) -> Iterator[Python]:
        for entry in self.finder.find_all_python_versions():
            yield Python(
                path=entry.path,
                version=entry.py_version.version,
                # TODO: detect implementation (How? From path?)
                implementation=python_implementation(),
            )

    @cached_property
    def _pythons(self) -> List[Python]:
        pythons = []
        for path in self.finder.get_pythons():
            pythons.append(Python(
                path=path,
                version=Version(self.finder.get_version(path)),
                # TODO: detect implementation (How? From path?)
                implementation=python_implementation(),
            ))
        pythons.sort(key=attrgetter('version'), reverse=True)
        return pythons

    # MAGIC METHODS

    def __iter__(self) -> Iterator[Python]:
        if not self.abstract:
            if isinstance(self.finder, WindowsFinder):
                yield from self._get_from_pythonfinder()
            else:
                yield from self._pythons
            return

        # return non-abstract pythons
        returned = set()
        non_abstract = type(self)(abstract=False)
        for version in PYTHONS:
            python = non_abstract.get_by_version(Version(version))
            if python is not None:
                returned.add(version)
                yield python

        # return abstract pythons for all python versions not in this system
        for version in PYTHONS:
            if version in returned:
                continue
            path = self.current.path
            name = 'python' + version
            yield Python(
                path=path.parent / (name + path.suffix),
                version=Version(version),
                implementation=self.current.implementation,
                abstract=True,
            )
