import json

from ._finder import Finder


finder = Finder()
pythons = []
for python in finder.get_pythons():
    pythons.append(dict(
        path=str(python),
        version=finder.get_version(python),
    ))
print(json.dumps(pythons, sort_keys=True, indent=2))
