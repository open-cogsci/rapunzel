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
from libqtopensesame.extensions import BaseExtension
from jupyter_tabwidget import ConsoleTabWidget
from qtpy.QtWidgets import QDockWidget
from qtpy.QtCore import Qt
from libqtopensesame.misc.translate import translation_context
_ = translation_context(u'JupyterConsole', category=u'extension')


class JupyterConsole(BaseExtension):

    def event_startup(self):

        self._jupyter_console = ConsoleTabWidget(self.main_window)
        self._dock_widget = QDockWidget(u'Console', self.main_window)
        self._dock_widget.setWidget(self._jupyter_console)
        self.main_window.addDockWidget(
            Qt.BottomDockWidgetArea,
            self._dock_widget
        )

    def event_jupyter_run_file(self, path):

        if not os.path.isfile(path):
            return
        self._jupyter_console.current.execute(
            u'%cd "{}"'.format(os.path.dirname(path))
        )
        self._jupyter_console.current.execute(
            u'%run "{}"'.format(path)
        )

    def event_jupyter_run_code(self, code):

        self._jupyter_console.current.execute(code)

    def event_jupyter_restart(self):

        self._jupyter_console.current.restart()

    def event_jupyter_interrupt(self):

        self._jupyter_console.current.interrupt()

    def event_jupyter_set_globals(self, global_dict):

        self._jupyter_console.current.set_globals(global_dict)

    def event_jupyer_get_globals(self):

        return self._jupyter_console.current.get_globals()

    def event_close(self):

        self._jupyter_console.close_all()
