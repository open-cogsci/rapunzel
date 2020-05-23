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
from libqtopensesame.misc.config import cfg
from pyqode.core import modes
from pyqode.core.api.utils import TextHelper
from qtpy.QtWidgets import QAction
from libqtopensesame.misc.translate import translation_context
_ = translation_context('SpellCheck', category='extension')


class SpellCheck(BaseExtension):
    
    preferences_ui = 'extensions.SpellCheck.preferences'

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

    def event_startup(self):

        try:
            self._mimetypes = [
                safe_decode(s)
                for s in cfg.spellcheck_mimetypes.split(';')
            ]
        except Exception as e:
            oslogger.debug('failed to parse mimetypes: {}'.format(e))
            self._mimetypes = []
        oslogger.debug('enabling spellcheck for {}'.format(self._mimetypes))
        
    def _ignore_list(self):
        
        ignore = cfg.spellcheck_ignore
        if not isinstance(ignore, str):
            return []
        return ignore.split(u';')

    def _set_language(self, language, editor=None):

        # Getting the current editor if none was given
        if editor is None:
            if 'OpenSesameIDE' not in self.extension_manager:
                oslogger.warning('SpellCheck requires OpenSesameIDE')
                return
            editor = self.extension_manager['OpenSesameIDE']._current_editor()
            if editor is None:
                return
        if 'SpellCheckerMode' in editor.modes.keys():
            editor.modes.remove('SpellCheckerMode')
            if hasattr(editor, 'action_ignore_word'):
                editor.action_ignore_word.triggered.disconnect(
                    self._ignore_current
                )
                editor.remove_action(
                    editor.action_ignore_word,
                    sub_menu=_('Spell checking')
                )
                editor.action_clear_ignore.triggered.disconnect(
                    self._clear_ignore
                )
                editor.remove_action(
                    editor.action_clear_ignore,
                    sub_menu=_('Spell checking')
                )
        if language is None:
            return  # disable spell checker
        try:
            import spellchecker
        except ImportError:
            oslogger.warning('failed to import spellchecker')
            self.extension_manager.fire(
                'notify',
                message=_('Please install pyspellchecker for spell checking')
            )
            return
        oslogger.debug('enabling spellcheck for {}'.format(editor))
        spellchecker = modes.SpellCheckerMode()
        spellchecker.add_extra_info('language', language)
        spellchecker.add_extra_info('ignore', self._ignore_list())
        editor.modes.append(spellchecker)
        # Add context menu actions
        editor.action_ignore_word = QAction(
            _('Add word to custom dictionary'),
            editor
        )
        editor.action_ignore_word.triggered.connect(self._ignore_current)
        editor.add_action(
            editor.action_ignore_word,
            sub_menu=_('Spell checking')
        )
        editor.action_clear_ignore = QAction(
            _('Clear custom dictionary'),
            editor
        )
        editor.action_clear_ignore.triggered.connect(self._clear_ignore)
        editor.add_action(
            editor.action_clear_ignore,
            sub_menu=_('Spell checking')
        )
        
    def _refresh_ignore(self):
        
        if 'pyqode_manager' not in self.extension_manager:
            oslogger.warning('SpellCheck requires pyqode_manager')
            return
        for editor in self.extension_manager['pyqode_manager']._editors:
            if 'SpellCheckerMode' not in editor.modes.keys():
                continue
            spellchecker_mode = editor.modes.get('SpellCheckerMode')
            spellchecker_mode.add_extra_info(
                'ignore',
                self._ignore_list()
            )
            spellchecker_mode.request_analysis()
            
    def _ignore_current(self):
        
        word = self.extension_manager.provide('ide_current_word')
        if not word:
            return
        cfg.spellcheck_ignore = u';'.join(self._ignore_list() + [word])
        self._refresh_ignore()
            
    def _clear_ignore(self):
        
        cfg.spellcheck_ignore = u''
        self._refresh_ignore()

    def event_register_editor(self, editor):

        if editor.language not in self._mimetypes:
            return
        self._set_language(cfg.spellcheck_default_language, editor)
