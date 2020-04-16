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
from libqtopensesame.misc.translate import translation_context
from data_viewer_file_handlers import BaseFileHandler
_ = translation_context(u'DataViewer', category=u'extension')


class PythonFileHandler(BaseFileHandler):
    
    def csv(self):
        
        return self._open_csv, _('Load into workspace (DataMatrix) and view')
    
    def xlsx(self):
        
        return self._open_xlsx, _('Load into workspace (DataMatrix) and view')
    
    def png(self):
        
        return self._open_image, _('Load into workspace (PIL image) and view')
    
    def jpg(self):
        
        return self._open_image, _('Load into workspace (PIL image) and view')
    
    def jpeg(self):
        
        return self._open_image, _('Load into workspace (PIL image) and view')
        
    def open_in_workspace(self, code, path, tmpl):
        
        symbol = BaseFileHandler.open_in_workspace(self, code, path, tmpl)
        self._data_viewer.queue.append(symbol)
        return symbol

    def _open_csv(self, path):
        
        self.open_in_workspace(
            code=(
                'from datamatrix import io\n'
                '{symbol} = io.readtxt(r"{path}")'
            ),
            path=path,
            tmpl='csv_{}'
        )
        
    def _open_xlsx(self, path):
        
        self.open_in_workspace(
            code=(
                'from datamatrix import io\n'
                '{symbol} = io.readxlsx(r"{path}")'
            ),
            path=path,
            tmpl='xlsx_{}'
        )
        
    def _open_image(self, path):
        
        self.open_in_workspace(
            code=(
                'from PIL import Image\n'
                '{symbol} = Image.open(r"{path}")'
            ),
            path=path,
            tmpl='img_{}'
        )
