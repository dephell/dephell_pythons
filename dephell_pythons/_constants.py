import os
import platform


IS_WINDOWS = (os.name == 'nt' or platform.system() == 'Windows')

PYTHONS_DEPRECATED = ('2.6', '2.7', '3.0', '3.1', '3.2', '3.3', '3.4')
PYTHONS_POPULAR = ('3.5', '3.6', '3.7')
PYTHONS_UNRELEASED = ('3.8', '4.0')
PYTHONS = PYTHONS_POPULAR + tuple(reversed(PYTHONS_DEPRECATED)) + PYTHONS_UNRELEASED

PYTHON_IMPLEMENTATIONS = (
    'python',
    'ironpython',
    'jython',
    'pypy',
    'anaconda',
    'miniconda',
    'stackless',
    'activepython',
    'micropython',
)

SUFFIX_PATTERNS = (
    '?',
    '?.?',
    '?.?m',
    '?-?.?',
    '?-?.?.?',
    '?.?-?.?.?',
)
