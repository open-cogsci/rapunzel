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
from libqtopensesame.extensions import BaseExtension
from libopensesame.oslogging import oslogger
from pyqode.core import modes


class SpellCheck(BaseExtension):

    def activate(self):

        self.extension_manager.fire(
            u'quick_select',
            haystack=[
                (_('Disable'), None, self._set_language),
                (_('English'), 'en', self._set_language),
                (_('French'), 'fr', self._set_language),
                (_('German'), 'de', self._set_language),
                (_('Portuguese'), 'pt', self._set_language),
                (_('Spanish'), 'es', self._set_language)
            ],
            placeholder_text=_(u'Set language for spell checking …')
        )

    def _set_language(self, language):

        if 'OpenSesameIDE' not in self.extension_manager:
            oslogger.warning('SpellCheck requires OpenSesameIDE')
            return
        editor = self.extension_manager['OpenSesameIDE']._current_editor()
        if editor is None:
            return
        if 'SpellCheckerMode' in editor.modes.keys():
            editor.modes.remove('SpellCheckerMode')
        if language is not None:
            spellchecker = modes.SpellCheckerMode()
            spellchecker.set_ignore_rules(language)
            editor.modes.append(spellchecker)
