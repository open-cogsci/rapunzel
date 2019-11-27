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

from libopensesame.py3compat import *
from datamatrix import DataMatrix
from data_viewer_inspectors.inspect_DataMatrix import inspect_DataMatrix
from data_viewer_inspectors.inspect_list import inspect_list


def inspect_ndarray(value):

    if len(value.shape) == 1:
        return inspect_list(value)
    if len(value.shape) == 2:
        rows, cols = value.shape
        dm = DataMatrix(length=rows)
        for col in range(cols):
            dm['col{:05d}'.format(col)] = value[:, col]
        return inspect_DataMatrix(dm)
    raise ValueError('Can only inspect 1D and 2D arrays')
