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
            python.lib_paths = self._get_lib_paths(env)
            pythons.append(python)
        return pythons

    @staticmethod
    def _get_lib_paths(env) -> List[Path]:
        paths = []
        libs = env.info._d['PythonPath']._d[''].split(';')
        for path in libs:
            path = Path(path)
            if 'Scripts' not in path.parts:
                paths.append(path)
        return paths
