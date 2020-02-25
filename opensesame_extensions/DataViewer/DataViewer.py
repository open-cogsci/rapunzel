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
        self._queue = []

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
        
    def provide_open_file_extension_csv(self):
        
        return self._open_csv, _('Load into workspace (DataMatrix) and view')
    
    def provide_open_file_extension_xlsx(self):
        
        return self._open_xlsx, _('Load into workspace (DataMatrix) and view')
    
    def provide_open_file_extension_png(self):
        
        return self._open_image, _('Load into workspace (PIL image) and view')
    
    def provide_open_file_extension_jpg(self):
        
        return self._open_image, _('Load into workspace (PIL image) and view')
    
    def provide_open_file_extension_jpeg(self):
        
        return self._open_image, _('Load into workspace (PIL image) and view')
    
    def remove_dock_widget(self, name):
        
        if name in self._dock_widgets:
            del self._dock_widgets[name]
            
    def event_workspace_update(self, name, workspace_func):

        self._update(name)
        # The queue contains symbol names that should be shown after the next
        # kernel command has been executed. This allows for loading files from
        # disk with a command, and then subsequently showing them.
        while self._queue:
            symbol = self._queue.pop()
            self.extension_manager.fire(
                'data_viewer_inspect',
                name=symbol,
                workspace=self.extension_manager.provide(
                    'jupyter_workspace_name'
                )
            )

    def event_workspace_restart(self, name, workspace_func):

        self._update(name)

    def event_workspace_switch(self, name, workspace_func):

        self._update(name)

    def event_workspace_new(self, name, workspace_func):

        self._update(name)            
    
    def _unique_symbol(self, tmpl):
        
        workspace_list = self.extension_manager.provide(
            'jupyter_list_workspace_globals'
        )
        i = 0
        while tmpl.format(i) in workspace_list:
            i += 1
        return tmpl.format(i)
        
    def _open_in_workspace(self, code, path, tmpl):
        
        symbol = self._unique_symbol(tmpl)
        self.extension_manager.fire(
            'jupyter_run_code',
            code=code.format(path=path, symbol=symbol)
        )
        self._queue.append(symbol)

    def _open_csv(self, path):
        
        self._open_in_workspace(
            code=(
                'from datamatrix import io\n'
                '{symbol} = io.readtxt(r"{path}")'
            ),
            path=path,
            tmpl='csv_{}'
        )
        
    def _open_xlsx(self, path):
        
        self._open_in_workspace(
            code=(
                'from datamatrix import io\n'
                '{symbol} = io.readxlsx(r"{path}")'
            ),
            path=path,
            tmpl='xlsx_{}'
        )
        
    def _open_image(self, path):
        
        self._open_in_workspace(
            code=(
                'from PIL import Image\n'
                '{symbol} = Image.open(r"{path}")'
            ),
            path=path,
            tmpl='img_{}'
        )
                    
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
