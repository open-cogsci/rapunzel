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
import importlib
from libqtopensesame.extensions import BaseExtension
from libopensesame.oslogging import oslogger
from libqtopensesame.misc.translate import translation_context
from qtpy.QtWidgets import QDockWidget
from qtpy.QtCore import Qt
from data_viewer_inspectors.inspect_str import inspect_str
_ = translation_context(u'DataViewer', category=u'extension')


class DataViewer(BaseExtension):

    def event_data_viewer_inspect(self, name, value):

        self.main_window.set_busy(True)
        cls = value.__class__.__name__
        fnc = self._inspect_fnc(cls)
        try:
            widget = fnc(value)
        except Exception as e:
            oslogger.debug('failed to inspect {}: {}'.format(name, e))
            widget = self._inspect_fallback(value)
        dw = QDockWidget(self.main_window)
        dw.setWidget(widget)
        dw.setWindowTitle('Variable: {} ({})'.format(name, cls))
        self.main_window.addDockWidget(Qt.RightDockWidgetArea, dw)
        self.main_window.set_busy(False)

    def _inspect_fnc(self, cls):

        try:
            m = importlib.import_module(
                'data_viewer_inspectors.inspect_{}'.format(cls)
            )
        except ModuleNotFoundError:
            oslogger.debug('using fallback inspector for type {}'.format(cls))
            return self._inspect_fallback
        else:
            oslogger.debug('using dedicated inspector for type {}'.format(cls))
        return getattr(m, 'inspect_{}'.format(cls))

    def _inspect_fallback(self, value):

        return inspect_str(repr(value))
