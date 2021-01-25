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

MARKDOWN_CELL = u'# <markdowncell>\n"""\n{}\n"""\n# </markdowncell>\n'
CODE_CELL = u'# <codecell>\n{}\n# </codecell>\n'
# Matches <codecell> ... </codecell> and <markdowncell> ... </markdowncell>
NOTEBOOK_PATTERN = r'^#[ \t]*<(?P<cell_type>code|markdown)cell>[ \t]*\n(?P<source>.*?)\n^#[ \t]*</(code|markdown)cell>'
# Matches # %% .. # %%
SPYDER_PATTERN = r'((#[ \t]*%%[ \t]*\n)|\A)(?P<markdown>.*?)\n(?!#)(?P<source>.*?)(\n|\Z)((?=#[ \t]*%%[ \t]*(\n|\Z))|\Z)'
# Matches based on multiline strings """ or '''
SIMPLE_PATTERN = r'^["\']{3}[ \t]*\n(?P<source>.*?)\n["\']{3}[ \t]*\n'
# To check whether there any Spyder cells in there
SPYDER_HAS_CELLS = r'#[ \t]*%%[ \t]*(\n|\Z)'
# Finds output `# % output` blocks in the code cells
OUTPUT_PATTERN = r'\n# % output[ \t]*\n(?P<output>.*?)(\n|\Z)(?!#)'
# Matches ``` and ~~~ for code blocks embedded in Markdown
FENCED_BLOCK_RE = re.compile(
r'''
(?P<fence>^(?:~{3,}|`{3,}))[ ]*                      # opening fence
((\{(?P<attrs>[^\}\n]*)\})?|                         # (optional {attrs} or
(\.?(?P<lang>[\w#.+-]*))?[ ]*                        # optional (.)lang
(hl_lines=(?P<quot>"|')(?P<hl_lines>.*?)(?P=quot))?) # optional hl_lines)
[ ]*\n                                               # newline (end of opening fence)
(?P<code>.*?)(?<=\n)                                 # the code block
(?P=fence)[ ]*$                                      # closing fence
''', re.MULTILINE | re.DOTALL | re.VERBOSE)


def parse_python(code=u'', cell_types=None):

    cells = []
    # Notebook type cells
    for m in re.finditer(NOTEBOOK_PATTERN, code, re.MULTILINE | re.DOTALL):
        if (
            cell_types is not None and
            m.group('cell_type') not in cell_types
        ):
            continue
        cells.append({
            'cell_type': m.group('cell_type'),
            'source': m.group('source'),
            'start': m.start(),
            'end': m.end()
        })
    if cells:
        return _separate_output(cells)
    # Spyder type cells. We only search for those if there's at least one
    # Spyder cell definition in the code, because otherwise we match the
    # entire code.
    if (
        (cell_types is None or 'code' in cell_types) and
        re.search(SPYDER_HAS_CELLS, code, re.DOTALL) is not None
    ):
        for m in re.finditer(
            SPYDER_PATTERN,
            code,
            re.MULTILINE | re.DOTALL
        ):
            markdown = ''
            for md_line in m.group('markdown').splitlines():
                markdown += md_line[1:].lstrip()
            if markdown:
                cells.append({
                    'cell_type': 'markdown',
                    'source': markdown,
                    'start': m.start('markdown'),
                    'end': m.end('markdown')
                })
            cells.append({
                'cell_type': 'code',
                'source': m.group('source'),
                'start': m.start('source'),
                'end': m.end('source')
            })
    if cells:
        return _separate_output(cells)
    # Simple cells, separated by triple quotes
    end_prev = 0
    for m in re.finditer(SIMPLE_PATTERN, code, re.MULTILINE | re.DOTALL):
        # Code cells in between two comments
        if cell_types is None or u'code' in cell_types:
            codecell = code[end_prev:m.start()]
            # Ignore empty codecells at the beginning
            if codecell or end_prev:
                cells.append({
                    'cell_type': 'code',
                    'source': codecell,
                    'start': end_prev,
                    'end': m.start()
                })
        if cell_types is None or u'markdown' in cell_types:
            cells.append({
                'cell_type': 'markdown',
                'source': m.group('source'),
                'start': m.start(),
                'end': m.end()
            })
        end_prev = m.end()
    # The last code cell that is not followed by a comment
    if (
        (cell_types is None or u'code' in cell_types) and
        end_prev not in (len(code) - 1, 0)
    ):
        codecell = code[end_prev:]
        if codecell:
            cells.append({
                'cell_type': 'code',
                'source': codecell,
                'start': end_prev,
                'end': len(code),
            })
    return _separate_output(cells)


def _separate_output(cells):
    """Code cells can have output embedded in them as code comments preceded by
    a `# % output` marker. Detecte these and split the code cell up into code
    cells and output cells.
    """

    new_cells = []
    execution_count = 1
    for cell in cells:
        if cell['cell_type'] != 'code':
            new_cells.append(cell)
            continue
        source = cell['source']
        prev_start = 0
        for m in re.finditer(
            OUTPUT_PATTERN,
            source,
            re.MULTILINE | re.DOTALL
        ):
            new_cells.append({
                'cell_type': 'code',
                'source': source[prev_start:m.start()].strip(),
                'execution_count': execution_count,
                'start': prev_start + cell['start'],
                'end': m.start() + cell['start'],
                "output_type": "execute_result",
                'outputs': m.group('output')
            })
            execution_count += 1
            prev_start = m.end()
        # There may a trailing cell behind the last output block. If this
        # is not empty, we insert it as a new cell. If no code/ output
        # cells were detected yet, we also insert it, even if it's empty,
        # because then it was a proper empty code cell to begin with.
        code = source[prev_start:].strip()
        if not prev_start and code:
            new_cells.append({
                'cell_type': 'code',
                'source': code,
                'start': prev_start + cell['start'],
                'end': len(source) + cell['start']
            })
    return new_cells
