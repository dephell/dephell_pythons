# built-in
from pathlib import Path

# external
import attr
from packaging.version import Version


@attr.s(slots=True)
class Python:
    path = attr.ib(type=Path)
    version = attr.ib(type=Version)
    name = attr.ib(type=str)
    implementation = attr.ib(type=str)
    abstract = attr.ib(type=bool, default=False)

    def get_short_version(self, size=2) -> Version:
        numbers = map(str, self.version.release[:size])
        return Version('.'.join(numbers))
