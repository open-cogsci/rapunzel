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
import subprocess
from libqtopensesame.misc.config import cfg
from libqtopensesame.extensions import BaseExtension
from libqtopensesame.misc.translate import translation_context
_ = translation_context(u'GitGUI', category=u'extension')


class GitGUI(BaseExtension):

    def activate(self):

        current_path = self.extension_manager.provide('ide_current_path')
        if current_path is not None:
            current_path = os.path.dirname(current_path)
        try:
            subprocess.Popen(
                cfg.git_gui_executable.split(),
                cwd=current_path
            )
        except Exception as e:
            self.notify(_(
                u'Failed to launch Git GUI. '
                u'See debug window for error message.'
            ))
            self.console.write(e)
