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
from libopensesame.oslogging import oslogger
from qtpy.QtWidgets import QDockWidget
from qtpy.QtCore import Qt
from data_viewer_inspectors.inspect_str import inspect_str


class DataDockWidget(QDockWidget):
    
    def __init__(self, data_viewer, name, value, workspace):
        
        QDockWidget.__init__(self, data_viewer.main_window)
        self._data_viewer = data_viewer
        self._name = name
        self._workspace = workspace
        self.setObjectName('DataDockWidget_{}'.format(name))
        self.refresh(value)
        
    @property
    def workspace(self):
        
        return self._workspace
        
    def refresh(self, value):
        
        self._value = value
        cls = self._value.__class__.__name__
        fnc = self._inspect_fnc(cls)
        try:
            widget = fnc(value)
        except Exception as e:
            oslogger.debug('failed to inspect {}: {}'.format(self._name, e))
            widget = self._inspect_fallback(value)
        self.setWidget(widget)
        self.setWindowTitle('{}: {}'.format(self._name, cls))

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

    def closeEvent(self, e):

        self._data_viewer.remove_dock_widget(self._name)
        self.close()
