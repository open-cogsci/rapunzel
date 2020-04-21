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

from data_viewer_file_handlers._base_file_handler import BaseFileHandler
from data_viewer_file_handlers._python_file_handler import PythonFileHandler
from data_viewer_file_handlers._ir_file_handler import IrFileHandler
# The Python kernel has different names
Python3FileHandler = Python2FileHandler = PythonFileHandler
