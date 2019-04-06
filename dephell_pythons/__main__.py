from ._finder import Finder


for python in Finder().get_pythons():
    print(str(python))
