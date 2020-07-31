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
from libqtopensesame.misc.translate import translation_context
_ = translation_context(u'WordCount', category=u'extension')


class WordCount(BaseExtension):

    def activate(self):

        source = self.extension_manager.provide('ide_current_selection')
        if not source:
            source = self.extension_manager.provide('ide_current_source')
        if source:
            message = _('{} lines, {} words, {} characters').format(
                source.count('\n') + 1,
                len(source.split()),
                len(source)
            )
        else:
            message = _('Nothing to count')
        self.extension_manager.fire(
            'notify',
            message=message,
            always_show=True
        )
