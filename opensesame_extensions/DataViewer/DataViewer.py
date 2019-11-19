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
from libqtopensesame.extensions import BaseExtension
from libqtopensesame.misc.config import cfg
from libopensesame.oslogging import oslogger
from libqtopensesame.misc.translate import translation_context
from datamatrix import DataMatrix, convert as cnv
from qdatamatrix import QDataMatrix
import json
from qtpy.QtWidgets import QDockWidget, QLabel, QScrollArea
from qtpy.QtGui import QFont
from qtpy.QtCore import Qt
_ = translation_context(u'DataViewer', category=u'extension')


class DataViewer(BaseExtension):

    def event_data_viewer_inspect(self, name, value):

        self.main_window.set_busy(True)
        cls = value.__class__.__name__
        fnc = '_inspect_{}'.format(cls)
        oslogger.debug('inspecting value of type {}'.format(cls))
        try:
            widget = getattr(self, fnc)(value)
        except Exception as e:
            oslogger.debug('failed to inspect {}: {}'.format(name, e))
            widget = self._inspect_fallback(value)
        dw = QDockWidget(self.main_window)
        dw.setWidget(widget)
        dw.setWindowTitle('Variable: {}'.format(name))
        self.main_window.addDockWidget(Qt.RightDockWidgetArea, dw)
        self.main_window.set_busy(False)

    def _inspect_list(self, value):

        dm = DataMatrix(length=len(value))
        dm.values = value
        return self._inspect_DataMatrix(dm)

    def _inspect_tuple(self, value):

        return self._inspect_list(value)

    def _inspect_set(self, value):

        return self._inspect_list(value)

    def _inspect_DataFrame(self, value):

        return self._inspect_DataMatrix(cnv.from_pandas(value))

    def _inspect_DataMatrix(self, value):

        return QDataMatrix(value, read_only=True)

    def _inspect_ndarray(self, value):

        if len(value.shape) == 1:
            return self._inspect_list(value)
        if len(value.shape) == 2:
            rows, cols = value.shape
            dm = DataMatrix(length=rows)
            for col in range(cols):
                dm['col{:05d}'.format(col)] = value[:, col]
            return self._inspect_DataMatrix(dm)
        raise ValueError('Can only inspect 1D and 2D arrays')

    def _inspect_text(self, value):

        widget = QScrollArea(self.main_window)
        label = QLabel(widget)
        label.setWordWrap(True)
        label.setText(value)
        label.setFont(QFont(cfg.pyqode_font_name, cfg.pyqode_font_size))
        widget.setWidget(label)
        return widget

    def _inspect_dict(self, value):

        return self._inspect_text(json.dumps(value, indent='  '))

    def _inspect_fallback(self, value):

        return self._inspect_text(repr(value))
