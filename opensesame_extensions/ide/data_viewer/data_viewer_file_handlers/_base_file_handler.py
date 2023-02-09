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
from libqtopensesame.misc.base_subcomponent import BaseSubcomponent


class BaseFileHandler(BaseSubcomponent):
    
    supported_extensions = 'csv', 'xlsx', 'png', 'jpg', 'jpeg'
    
    def __init__(self, data_viewer):
        
        self._data_viewer = data_viewer
        self.setup(data_viewer)

    def open_in_workspace(self, code, path, tmpl):
        
        symbol = self._unique_symbol(tmpl)
        self.extension_manager.fire(
            'jupyter_run_code',
            code=code.format(path=path, symbol=symbol)
        )
        return symbol

    def _unique_symbol(self, tmpl):
        
        workspace_list = self.extension_manager.provide(
            'jupyter_list_workspace_globals'
        )
        i = 0
        while tmpl.format(i) in workspace_list:
            i += 1
        return tmpl.format(i)
