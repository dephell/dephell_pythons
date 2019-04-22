import json

from ._finder import Finder


finder = Finder()
pythons = []
for path in finder.get_pythons():
    pythons.append(dict(
        path=str(path),
        version=finder.get_version(path),
        shim=finder.in_shims(path=path),
    ))
print(json.dumps(pythons, sort_keys=True, indent=2))
