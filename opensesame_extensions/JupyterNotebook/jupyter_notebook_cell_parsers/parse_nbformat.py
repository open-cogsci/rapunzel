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
import nbformat
import base64
from libopensesame.oslogging import oslogger


def notebook_to_code(path, img_to_file_fnc):
    """Reads an ipynb file and turns it into code with cell markers."""
    nb = nbformat.read(path, as_version=4)
    py_cells = []
    for cell in nb['cells']:
        if cell['cell_type'] == 'markdown':
            py_cells.append(u'"""\n{}\n"""\n'.format(cell['source']))
        elif cell['cell_type'] == 'code':
            py_cells.append(cell['source'] + u'\n')
            if cell['outputs']:
                py_cells += ['# % output']
            for output in cell['outputs']:
                if 'text' in output:  # Convert to data-style format
                    py_cells += _output_cell_to_code(
                        {'text/plain': output['text']},
                        img_to_file_fnc
                    )
                elif 'data' in output:
                    py_cells += _output_cell_to_code(
                        output['data'],
                        img_to_file_fnc
                    )
    code = u'\n'.join(py_cells)
    if not code.endswith('\n'):
        code += '\n'
    return code


def cells_to_notebook(cells, path=None):
    """Takes a list of cells as returned by one of the cell parsers, and turns
    it into a notebook object. If a path is specified, the notebook is written
    to file, otherwise it is returned as an object.
    """
    nb = nbformat.v4.new_notebook()
    for pycell in cells:
        cell = {
            'cell_type': pycell['cell_type'],
            'source': pycell['source'],
            'metadata': {}
        }
        if pycell['cell_type'] == 'code':
            if 'execution_count' in pycell:
                cell['execution_count'] = pycell['execution_count']
                cell['outputs'] = _notebook_output_cells(
                    pycell['outputs'],
                    pycell['execution_count']
                )
            else:
                cell['execution_count'] = 0
                cell['outputs'] = []
        elif pycell['cell_type'] == 'markdown':
            cell['source'] = \
                cell['source'].lstrip(u'"""\n').rstrip(u'\n"""')
        nb['cells'].append(nbformat.from_dict(cell))
    if path is None:
        return nb
    nbformat.write(nb, path)
    
    
def _output_cell_to_code(data, img_to_file_fnc):

    code = []
    for fmt, content in data.items():
        if fmt == 'text/plain':
            if isinstance(content, str):
                content = content.splitlines()
            code += ['# {}'.format(line) for line in content]
        elif img_to_file_fnc is None:
            code += ['# Warning: Enable output capture to render images']
        else:
            try:
                path = img_to_file_fnc(base64.b64decode(content), fmt)
            except ValueError:
                code += ['# Warning: Unknown object of format {}'.format(fmt)]
            else:
                code += ['# ![]({})'.format(path)]
    return code


def _notebook_output_cell(type_, data, execution_count):
    
    return {
        'data': {type_: data},
        'execution_count': execution_count,
        'metadata': {},
        'output_type': 'execute_result'
    }


def _notebook_img_cell(type_, img_path, execution_count):
        
    base, ext = os.path.splitext(img_path.lower())
    if ext == '.png':
        fmt = 'image/png'
    elif ext in ('.jpg', '.jpeg'):
        fmt = 'image/jpeg'
    elif ext == '.svg':
        fmt = 'image/svg+xml'
    else:
        oslogger.warning('unknown image format: {}'.format(img_path))
        return {}
    with open(img_path, 'rb') as fd:
        data = base64.b64encode(fd.read())
    return _notebook_output_cell(fmt, data, execution_count)


def _notebook_output_cells(output, execution_count):
    
    data = []
    outputs = []
    for line in output.splitlines():
        if line.startswith('# ![]'):
            if data:
                outputs.append(
                    _notebook_output_cell(
                        'text/plain',
                        '\n'.join(data),
                        execution_count
                    )
                )
                data = []
            img_path = line.rstrip()[6:-1]
            outputs.append(
                _notebook_img_cell(
                    'image/png',
                    img_path,
                    execution_count
                )
            )
            continue
        if line.startswith('# '):
            line = line[2:]
        elif line.startswith('#'):
            line = line[1:]
        data.append(line)
    if data:
        outputs.append(
            _notebook_output_cell(
                'text/plain',
                '\n'.join(data),
                execution_count
            )
        )
    return outputs
