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
from jupyter_notebook_cell_parsers.parse_python import FENCED_BLOCK_RE


def _markdown_cells(code=u'', cell_types=None):
    
    cells = []
    offset = 0
    while True:
        m = FENCED_BLOCK_RE.search(code)
        if not m:
            break
        chunk = code[m.start():m.end()]
        start = m.start() + offset + chunk.find(u'\n') + 1
        end = m.start() + offset + chunk.rfind(u'\n')
        cells.append({
            'cell_type': 'code',
            'source': m.group('code'),
            'start': start,
            'end': end
        })
        offset += m.end()
        code = code[m.end():]
    return cells
