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
from libopensesame.oslogging import oslogger
from libqtopensesame.extensions import BaseExtension
from libqtopensesame.misc.translate import translation_context
_ = translation_context(u'SymbolSelector', category=u'extension')


PYTHON_SYMBOLS = r'^[ \t]*(?P<type>def|class)[ \t]+(?P<name>\w+)'
R_SYMBOLS = r'^[ \t]*(?P<name>[\w.]+)[ \t]*<-[ \t]*function'
MARKDOWN_HEADINGS = r'^#+[ \t]*(?P<name>.+)$'
MARKDOWN_HR = r'^---[ \t]*\n[ \t\n]*(?P<name>.{1,50})'


class SymbolSelector(BaseExtension):
    
    preferences_ui = 'extensions.SymbolSelector.preferences'

    def activate(self):

        self.main_window.set_busy(True)
        editor = self.extension_manager.provide(u'ide_current_editor')
        haystack = []
        if editor is not None and 'SymbolsMode' in editor.modes.keys():
            lsp_symbols = editor.modes.get('SymbolsMode').request_symbols()
            for name, kind, lineno, container in lsp_symbols:
                if container is not None:
                    name = '{}.{}'.format(container, name)
                haystack.append((
                    name,
                    lineno + 1,
                    self._jump_to_line
                ))
        else:
            mimetype = self.extension_manager.provide(u'ide_current_language')
            try:
                fnc = getattr(self, u'_get_{}_symbols'.format(mimetype))
            except AttributeError:
                oslogger.warning(u'don\'t know how to handle {}'.format(mimetype))
                return
            symbols = fnc(self.extension_manager.provide(u'ide_current_source'))
            for name, lineno in symbols:
                haystack.append((name, lineno, self._jump_to_line))
        self.main_window.set_busy(False)
        self.extension_manager.fire(
            u'quick_select',
            haystack=haystack,
            placeholder_text=_(u'Search symbols in current file …')
        )

    def _jump_to_line(self, lineno):

        self.extension_manager.fire('ide_jump_to_line', lineno=lineno)
        
    def _linenr(self, code, pos):
        
        return code[:pos].count('\n') + 1

    def _get_symbols(self, pattern, code):

        return [
            (m.group('name'), self._linenr(code, m.start()))
            for m in re.finditer(
                pattern,
                code,
                re.MULTILINE | re.ASCII if py3 else re.MULTILINE
            )
        ]

    def _get_nameless_symbols(self, pattern, code, tmpl):

        return [
            (tmpl.format(i + 1), self._linenr(code, m.start()))
            for i, m in enumerate(re.finditer(
                pattern,
                code,
                re.MULTILINE | re.ASCII if py3 else re.MULTILINE
            ))
        ]

    def _get_python_symbols(self, code):

        return self._get_symbols(PYTHON_SYMBOLS, code)

    def _get_R_symbols(self, code):

        return self._get_symbols(R_SYMBOLS, code)

    def _get_markdown_symbols(self, code):

        return (
            self._get_symbols(MARKDOWN_HEADINGS, code) +
            self._get_symbols(MARKDOWN_HR, code)
        )
        
    def _get_javascript_symbols(self, code):
        
        try:
            import esprima
        except ImportError:
            self.extension_manager.fire(
                'notify',
                message='Please install esprima for JavaScript support',
                category='warning'
            )
            return []
        from esprima.nodes import (
            ClassDeclaration,
            MethodDefinition,
            FunctionDeclaration
        )
        
        def parse_tree(ast):
            
            if isinstance(ast.body, list):
                symbols = []
                for e in ast.body:
                    symbols += parse_tree(e)
                return symbols
            if isinstance(
                ast.declaration,
                (ClassDeclaration, FunctionDeclaration)
            ):
                ast = ast.declaration
            if isinstance(ast, (ClassDeclaration, FunctionDeclaration)):
                return [(
                    ast.id.name,
                    self._linenr(code, ast.range[0])
                )] + parse_tree(ast.body)
            if isinstance(ast, MethodDefinition):
                return [(
                    ast.key.name,
                    self._linenr(code, ast.range[0])
                )] + parse_tree(ast.value.body)
            return []
        
        try:
            ast = esprima.parseScript(code, tolerant=True, range=True)
        except esprima.error_handler.Error:
            self.extension_manager.fire(
                'notify',
                message = 'Failed to parse JavaScript',
                category='warning'
            )
            return []
        return parse_tree(ast)

    def event_symbol_selector_activate(self):

        self.activate()
