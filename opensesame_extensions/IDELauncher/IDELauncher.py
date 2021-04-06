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
import sys
import subprocess
from libqtopensesame.misc.config import cfg
from libqtopensesame.extensions import BaseExtension
from libqtopensesame.misc.translate import translation_context
_ = translation_context(u'IDELauncher', category=u'extension')


class IDELauncher(BaseExtension):

    def activate(self):

        if cfg.ide_executable:
            cmd = cfg.ide_executable
        else:
            cmd = [sys.executable, sys.argv[0], '--mode=ide']
        try:
            subprocess.Popen(cmd)
        except Exception as e:
            self.notify(_(
                u'Failed to launch Code Editor. '
                u'See debug window for error message.'
            ))
            self.console.write(e)
