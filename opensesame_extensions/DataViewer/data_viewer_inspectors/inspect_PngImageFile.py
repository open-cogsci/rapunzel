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
import math
from PIL.ImageQt import ImageQt
from qtpy.QtGui import QPixmap
from qtpy.QtCore import QSize
from qtpy.QtWidgets import QLabel


class ImageLabel(QLabel):
    """Implements a label with a resizable image that maintains its original
    aspect ratio.
    """
    
    def __init__(self, img):
        
        QLabel.__init__(self)
        self._ratio = img.size[0] / img.size[1]
        self._pixmap = QPixmap.fromImage(ImageQt(img))
        self.setMinimumSize(QSize(10, 10))
        self.setScaledContents(True)
        self.setPixmap(self._pixmap)
        
    def resizeEvent(self, e):

        size = e.size()
        height = size.height()
        width = size.width()
        ratio = width / height
        if math.isclose(ratio, self._ratio):
            return
        if ratio > self._ratio:
            new_size = QSize(height * self._ratio, height)
        elif ratio < self._ratio:
            new_size = QSize(width, width / self._ratio)
        self.resize(new_size)


def inspect_PngImageFile(value):

    return ImageLabel(value)
