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
import os
import importlib
from qtpy.QtWidgets import QFileDialog
from libopensesame.oslogging import oslogger
from libqtopensesame.extensions import BaseExtension
from libqtopensesame.misc.config import cfg
from libqtopensesame.misc.translate import translation_context
_ = translation_context(u'JupyterNotebook', category=u'extension')


class JupyterNotebook(BaseExtension):
    """Handles various things related to JupyterLab:
    
    - Parses source code into cells, which are used for code execution by the
      OpenSesameIDE extension.
    - Allows code to be exported to, and imported from, ipynb format.
    - Allows JupyterLab to launched.
    """
    
    preferences_ui = 'extensions.JupyterNotebook.preferences'

    def event_startup(self):

        self.action_import_ipynb = self.qaction(
            u'document-open',
            _('Import notebook'),
            self._import_ipynb,
        )
        self.action_export_ipynb = self.qaction(
            u'document-save',
            _('Export notebook'),
            self._export_ipynb,
        )
        self._widget = None

    def event_close(self):

        if self._widget is None:
            return
        self._widget.kill()

    def activate(self):

        self.tabwidget.add(self.widget(), self.icon(), self.label())

    def widget(self):
        """A simple widget for launching and killing jupyterlab."""
        
        if self._widget is None:
            self.set_busy()
            from jupyter_widget import LaunchJupyterLabWidget
            self._widget = LaunchJupyterLabWidget(self.main_window, self)
            self.set_busy(False)
        return self._widget

    def provide_jupyter_notebook_cells(self, code=u'', cell_types=None):
        """Dynamically loads a parser function for the language of the current
        editor, and uses this to parse the code into cells. The `cell_types`
        keyword allows specific kinds of cells to be returned.
        """
        
        language = self.extension_manager.provide('ide_current_language')
        try:
            m = importlib.import_module(
                'jupyter_notebook_cell_parsers.parse_{}'.format(language)
            )
        except ModuleNotFoundError:
            oslogger.debug('no cell parser for language {}'.format(language))
            return
        return getattr(m, 'parse_{}'.format(language))(code, cell_types)
    
    def provide_open_file_extension_ipynb(self):
        """A provider for directly opening .ipynb files."""
        
        return self._import_ipynb, _('Import as Python script')
    
    def _import_ipynb(self, path=None):
        """Import an ipynb file from path and return it as plain-text code."""
        
        from jupyter_notebook_cell_parsers import parse_nbformat
        
        if path is None:
            path = QFileDialog.getOpenFileName(
                self.main_window,
                _(u'Open Jupyter/ IPython Notebook'),
                filter=u'Notebooks (*.ipynb)',
                directory=cfg.file_dialog_path
            )
        if isinstance(path, tuple):
            path = path[0]
        if not path:
            return
        cfg.file_dialog_path = os.path.dirname(path)
        try:
            code = parse_nbformat.notebook_to_code(
                path,
                self.extension_manager.provide('image_writer')
            )
        except Exception as e:
            self.extension_manager.fire(
                u'notify',
                message=_(u'Failed to read notebook. See console for details.')
            )
            self.console.write(e)
            return
        self.extension_manager.fire(u'ide_new_file', source=code)
        self.extension_manager.fire(u'image_annotations_detect', code=code)

    def _export_ipynb(self):
        """Export the code to an .ipynb file."""
        
        from jupyter_notebook_cell_parsers import parse_nbformat

        if self.extension_manager.provide('ide_current_language') != 'python':
            self.extension_manager.fire(
                'notify',
                message=_(u'Only Python code can be exported to a notebook')
            )
            return
        path = QFileDialog.getSaveFileName(
            self.main_window,
            _(u'Open Jupyter/ IPython Notebook'),
            filter=u'Notebooks (*.ipynb)',
            directory=cfg.file_dialog_path
        )
        if isinstance(path, tuple):
            path = path[0]
        if not path:
            return
        cfg.file_dialog_path = os.path.dirname(path)
        parse_nbformat.cells_to_notebook(
            self.provide_jupyter_notebook_cells(
                self.extension_manager.provide('ide_current_source')
            ),
            path
        )
