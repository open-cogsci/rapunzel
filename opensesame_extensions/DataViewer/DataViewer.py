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
from datadockwidget import DataDockWidget
_ = translation_context(u'DataViewer', category=u'extension')


class DataViewer(BaseExtension):
    
    def event_startup(self):
        
        self._dock_widgets = {}

    def event_data_viewer_inspect(self, name, workspace):

        if name in self._dock_widgets:
            return
        self.main_window.set_busy(True)
        value = self.extension_manager.provide(
            'jupyter_workspace_variable',
            name=name
        )        
        dw = DataDockWidget(self, name, value, workspace)
        self.main_window.addDockWidget(Qt.RightDockWidgetArea, dw)
        self.main_window.set_busy(False)
        self._dock_widgets[name] = dw
        
    def remove_dock_widget(self, name):
        
        if name in self._dock_widgets:
            del self._dock_widgets[name]
            
    def _update(self, name):

        # Only get the data for the current workspace
        dock_widgets = {
            name: dw
            for name, dw in self._dock_widgets.items()
            if dw.workspace != name
        }
        if not dock_widgets:
            return
        self.main_window.set_busy(True)
        workspace_list = None
        # Loop through all dockwidgets and get the current value of the
        # variable
        for name, dw in dock_widgets.items():
            value = self.extension_manager.provide(
                'jupyter_workspace_variable',
                name=name
            )
            # If the value is None, this can either mean that it is really None
            # or that the variable no longer exists. To check this, we get a
            # list of all global variables. However, for performance, we do
            # this only once, and only if it's necessary.
            if value is None:
                if workspace_list is None:
                    workspace_list = self.extension_manager.provide(
                        'jupyter_list_workspace_globals'
                    )
                # If the variable has been deleter, close the corresponding
                # dockwidget
                if name not in workspace_list:
                    dw.close()
                    continue
            dw.refresh(value)
        self.main_window.set_busy(False)

    def event_workspace_update(self, name, workspace_func):

        self._update(name)

    def event_workspace_restart(self, name, workspace_func):

        self._update(name)

    def event_workspace_switch(self, name, workspace_func):

        self._update(name)

    def event_workspace_new(self, name, workspace_func):

        self._update(name)
