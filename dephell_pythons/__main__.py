import json

from ._pythons import Pythons


pythons = []
for python in Pythons():
    pythons.append(dict(
        path=str(python.path),
        version=str(python.version),
        shim=python.shim,
    ))
print(json.dumps(pythons, sort_keys=True, indent=2))
