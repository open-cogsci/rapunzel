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
import re
import nbformat
from qtpy.QtWidgets import QFileDialog
from libqtopensesame.extensions import BaseExtension
from libqtopensesame.misc.translate import translation_context
_ = translation_context(u'JupyterNotebook', category=u'extension')

MARKDOWN_CELL = u'# <markdowncell>\n"""\n{}\n"""\n# </markdowncell>\n'
CODE_CELL = u'# <codecell>\n{}\n# </codecell>\n'
PATTERN = r'^# <(?P<cell_type>code|markdown)cell>\n(?P<source>.*?)\n^# </(code|markdown)cell>'


class JupyterNotebook(BaseExtension):

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

    def _import_ipynb(self):

        path = QFileDialog.getOpenFileName(
            self.main_window,
            _(u'Open Jupyter/ IPython Notebook'),
            filter=u'Notebooks (*.ipynb)'
        )
        if isinstance(path, tuple):
            path = path[0]
        if not path:
            return
        code = self._notebook_to_code(path)
        self.extension_manager.fire(u'ide_new_file', source=code)

    def _export_ipynb(self):

        path = QFileDialog.getSaveFileName(
            self.main_window,
            _(u'Open Jupyter/ IPython Notebook'),
            filter=u'Notebooks (*.ipynb)'
        )
        if isinstance(path, tuple):
            path = path[0]
        if not path:
            return
        code = self.extension_manager.provide(u'ide_current_source')
        self._code_to_notebook(code, path)

    def _notebook_to_code(self, path):

        nb = nbformat.read(path, as_version=4)
        py_cells = []
        for cell in nb['cells']:
            if cell['cell_type'] == 'markdown':
                py_cells.append(MARKDOWN_CELL.format(cell['source']))
            elif cell['cell_type'] == 'code':
                py_cells.append(CODE_CELL.format(cell['source']))
        return u'\n'.join(py_cells)

    def _code_to_notebook(self, code, path):

        nb = nbformat.v4.new_notebook()
        for m in re.finditer(PATTERN, code, re.MULTILINE | re.DOTALL):
            cell = {
                'cell_type': m.group('cell_type'),
                'source': m.group('source'),
                'metadata': {}
            }
            if m.group('cell_type') == 'code':
                cell['execution_count'] = 0
                cell['outputs'] = []
            elif m.group('cell_type') == 'markdown':
                cell['source'] = \
                    cell['source'].lstrip(u'"""\n').rstrip(u'\n"""')
            nb['cells'].append(nbformat.from_dict(cell))
        nbformat.write(nb, path)
