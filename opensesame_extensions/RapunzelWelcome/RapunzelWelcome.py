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
import sys
from libopensesame import misc, metadata
from libqtopensesame.extensions import BaseExtension
from libqtopensesame.misc.translate import translation_context
from libqtopensesame.misc import template_info
_ = translation_context(u'RapunzelWelcome', category=u'extension')


class RapunzelWelcome(BaseExtension):

    @BaseExtension.as_thread(wait=500)
    def event_startup(self):

        if self.extension_manager['OpenSesameIDE']._current_editor():
            # Only show the startup tab if no editors are open
            return
        with safe_open(self.ext_resource(u'rapunzel_welcome.md')) as fd:
            md = fd.read()
        self.tabwidget.open_markdown(
            md,
            title=_(u'Get started!'),
            icon=u'help-about'
        )
        self._widget = self.tabwidget.currentWidget()

    def event_rapunzel_welcome_open_folders(self):

        self.extension_manager['OpenSesameIDE'].quick_select_folders()

    def event_rapunzel_welcome_open_files(self):

        self.extension_manager['OpenSesameIDE'].quick_select_files()

    def event_register_editor(self, editor):

        if not hasattr(self, '_widget') or not self._widget:
            return
        index = self.tabwidget.indexOf(self._widget)
        self._widget = None
        if index < 0:
            return
        self.tabwidget.removeTab(index)
        self.extension_manager['OpenSesameIDE']._on_tabwidget_close(index)
