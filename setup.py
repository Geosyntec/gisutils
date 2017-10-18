# Setup script for the probscale package
#
# Usages
# install: python setup.py install
# run tests: python setup.py test [pytest args]
# configure vs code: python setup.py config [envname]

import os
import sys
from textwrap import indent
from setuptools import setup, find_packages


WINDOWS = """\
    "taskName": "test",
    "isBuildCommand": true,
    "isShellCommand": true,
    "isTestCommand": true,
    "command": "activate",
    "args": [
        "plmpy",
        "&&",
        "python",
        "setup.py",
        "test",
        "--cov",
        "--pep8"
    ]
"""

UNIX = """\
    "taskName": "test",
    "isBuildCommand": true,
    "isShellCommand": true,
    "isTestCommand": true,
    "command": "source",
    "args": [
        "activate",
        "plmpy",
        "&&",
        "python",
        "setup.py",
        "test",
        "--cov",
        "--pep8"
    ]
"""


TEMPLATE = """\
{{
    "version": "0.1.0",
    "isShellCommand": false,
    "args": [],
    "showOutput": "always",
    "echoCommand": false,
    "suppressTaskName": false,
    "tasks": [
        {{
{cmd:s}
        }},
        {{
            "taskName": "notebooks",
            "options": {{
                "cwd": "${{workspaceRoot}}/docs/tutorial"
            }},
            "command": "{pyexec:s}",
            "args": ["make.py"]
        }},
        {{
            "taskName": "docs",
            "options": {{
                "cwd": "${{workspaceRoot}}/docs"
            }},
            "command": "make.bat",
            "args": ["html"]
        }}
    ]
}}
"""

DESCRIPTION = "gisutils: miscellaneous GIS and mapping utilities"
LONG_DESCRIPTION = DESCRIPTION
NAME = "gisutils"
VERSION = "0.1.x"
AUTHOR = "Paul Hobson (Geosyntec Consultants)"
AUTHOR_EMAIL = "phobson@geosyntec.com"
URL = "https://github.com/Geosyntec/gisutils"
DOWNLOAD_URL = "https://github.com/Geosyntec/gisutils/archive/master.zip"
LICENSE = "BSD 3-clause"
PACKAGES = find_packages()
PLATFORMS = "Python 2.7, 3.4 and later."
CLASSIFIERS = [
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Intended Audience :: Science/Research",
    "Topic :: Software Development :: Libraries :: Python Modules",
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]
INSTALL_REQUIRES = ['numpy', 'matplotlib', 'shapely', 'fiona', 'rasterio', 'geopandas']
PACKAGE_DATA = {}


if sys.argv[1] == "test":
    import matplotlib
    matplotlib.use('agg')

    try:
        import pytest
    except ImportError as e:
        raise ImportError("`pytest` is required to run the test suite")
    sys.exit(pytest.main(sys.argv[2:]))

elif sys.argv[1] == "config":
    dirname = ".vscode"
    filename = "tasks.json"

    filepath = os.path.join(dirname, filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    if len(sys.argv) < 4:
        name = os.path.split(os.getcwd())[-1]
    else:
        name = sys.argv[3]

    if sys.platform.startswith('win'):
        cmd = WINDOWS
    else:
        cmd = UNIX

    prefix = ' ' * 8
    python = '/'.join(sys.executable.split(os.path.sep))
    config = TEMPLATE.format(cmd=indent(cmd, prefix), pyexec=python, modulename=name)

    with open(filepath, 'w') as configfile:
        configfile.write(config)
else:
    setup(
        name=NAME,
        version=VERSION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        download_url=DOWNLOAD_URL,
        license=LICENSE,
        packages=PACKAGES,
        package_data=PACKAGE_DATA,
        platforms=PLATFORMS,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        zip_safe=False,
    )
