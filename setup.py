#!/usr/bin/env python3
# coding=utf-8

"""
This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import fnmatch
import json
from setuptools import setup


EXCLUDE = [
    u'*~',
    u'*.pyc',
    u'*.pyo',
    u'*__pycache__*'
]

EXTENSIONS = [
    u'OpenSesameIDE',
    u'FindInFiles',
    u'JupyterConsole',
    u'JupyterNotebook',
    u'QuickSelector',
    u'WorkspaceExplorer',
    u'SymbolSelector',
    u'RapunzelWelcome',
    u'CommandPalette',
    u'WordCount',
    u'SpellCheck',
    u'DataViewer',
    u'GitGUI',
    u'RapunzelLocale',
    u'PythonDebugger',
    u'SubprocessManager',
    u'ImageAnnotations'
]


def is_excluded(path):

    return any(fnmatch.fnmatch(path, m) for m in EXCLUDE)


def recursive_glob(src_folder, target_folder):

    """
    desc:
        Recursively gets all files that are in src folder.

    arguments:
        src_folder:       The source folder.
        target_folder:    The target folder.

    returns:
        A list of (target folder, filenames) tuples.
    """

    globbed = []
    path_list = []
    for path in os.listdir(src_folder):
        full_path = os.path.join(src_folder, path)
        if is_excluded(full_path):
            continue
        if os.path.isdir(full_path):
            globbed += recursive_glob(
                full_path,
                os.path.join(target_folder, path)
            )
            continue
        path_list.append(full_path)
    globbed.append((os.path.join(u'share', target_folder), path_list))
    return globbed


def extensions():

    """
    desc:
        Create a list of all extension files that should be included.

    returns:
        A list of (target folder, filenames) tuples.
    """

    globbed = []
    for extension in EXTENSIONS:
        folder = os.path.join(u'opensesame_extensions', extension)
        globbed += recursive_glob(folder, folder)
    return globbed


def data_files():

    return (
        [
            (u"share/icons/hicolor/scalable/apps", [u"mime/rapunzel.svg"]),
            (u"share/applications", [u"mime/rapunzel.desktop"]),
        ] +
        extensions()
    )


def get_version():

    with open('opensesame_extensions/OpenSesameIDE/info.json') as fd:
        info = json.load(fd)
    return info['version']


setup(
    name='rapunzel',
    version=get_version(),
    description='Turns OpenSesame into a Python code editor',
    author='Sebastiaan Mathot',
    author_email='s.mathot@cogsci.nl',
    url='https://github.com/smathot/rapunzel',
    entry_points={
        'gui_scripts': [
            'rapunzel = rapunzel:rapunzel'
        ]
    },
    classifiers=[
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    py_modules=['rapunzel'],
    # The dependencies are ignored when invoked by stdeb3
    install_requires=(
        [] if 'install' in sys.argv and '--root' in sys.argv
        else [
            'python-levenshtein',
            'python-opensesame',
            'qtconsole',
            'nbformat',
            'pyspellchecker',
            'esprima',
            'psutil'
        ]
    ),
    data_files=data_files()
)
