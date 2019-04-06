from pathlib import Path
from typing import List

from packaging.version import Version

from ._cached_property import cached_property
from ._python import Python


class WindowsFinder:
    @cached_property
    def pythons(self) -> List[Python]:
        from .pep514tools import findall

        pythons = []
        for env in findall():
            python = Python(
                path=env.info._d['InstallPath'].executable_path,
                version=Version(str(env.info._d['Version'])),
                implementation='python',  # TODO: guess architecture
            )
            libs = env.info._d['PythonPath']._d[''].split(';')
            python.lib_paths = [Path(path) for path in libs]
            pythons.append(python)
        return pythons
