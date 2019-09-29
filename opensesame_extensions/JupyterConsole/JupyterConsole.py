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
from libqtopensesame.misc.config import cfg
from libqtopensesame.extensions import BaseExtension
from libopensesame.oslogging import oslogger
from jupyter_tabwidget import ConsoleTabWidget
from qtpy.QtWidgets import QDockWidget, QShortcut
from qtpy.QtCore import Qt
from qtpy.QtGui import QKeySequence
from libqtopensesame.misc.translate import translation_context
_ = translation_context(u'JupyterConsole', category=u'extension')


class JupyterConsole(BaseExtension):

    def event_startup(self):

        self._jupyter_console = ConsoleTabWidget(self.main_window)
        self._dock_widget = QDockWidget(u'Console', self.main_window)
        self._dock_widget.setObjectName(u'JupyterConsole')
        self._dock_widget.setWidget(self._jupyter_console)
        self._dock_widget.closeEvent = self._on_close_event
        self.main_window.addDockWidget(
            Qt.BottomDockWidgetArea,
            self._dock_widget
        )
        self._set_visible(cfg.jupyter_visible)
        self._shortcut_focus = QShortcut(
            QKeySequence(cfg.jupyter_focus_shortcut),
            self.main_window,
            self._focus,
            context=Qt.ApplicationShortcut
        )

    def activate(self):

        self._set_visible(not cfg.jupyter_visible)

    def event_run_experiment(self, fullscreen):

        oslogger.debug(u'capturing stdout')
        self._jupyter_console.current.capture_stdout()

    def event_end_experiment(self, ret_val):

        self._jupyter_console.current.release_stdout()
        self._jupyter_console.current.show_prompt()
        oslogger.debug(u'releasing stdout')

    def event_jupyter_run_file(self, path):

        self._set_visible(True)
        if not os.path.isfile(path):
            return
        self._jupyter_console.current.change_dir(os.path.dirname(path))
        self._jupyter_console.current.run_file(path)

    def event_jupyter_change_dir(self, path):

        self._jupyter_console.current.change_dir(path)

    def event_jupyter_run_code(self, code):

        self._set_visible(True)
        self._jupyter_console.current.execute(code)

    def event_jupyter_write(self, msg):

        try:
            self._jupyter_console.current.write(msg)
        except AttributeError:
            oslogger.error(safe_decode(msg))

    def event_jupyter_focus(self):

        self._jupyter_console.current.focus()

    def event_jupyter_show_prompt(self):

        self._jupyter_console.current.show_prompt()

    def event_jupyter_restart(self):

        self._jupyter_console.current.restart()

    def event_jupyter_interrupt(self):

        self._jupyter_console.current.interrupt()

    def event_set_workspace_globals(self, global_dict):

        self._jupyter_console.current.set_workspace_globals(global_dict)

    def provide_jupyter_workspace_name(self):

        return self._jupyter_console.current.name

    def provide_jupyter_workspace_globals(self):

        return self.get_workspace_globals()

    def get_workspace_globals(self):

        return self._jupyter_console.current.get_workspace_globals()

    def event_close(self):

        self._jupyter_console.close_all()

    def _set_visible(self, visible):

        cfg.jupyter_visible = visible
        self.set_checked(visible)
        if visible:
            self._dock_widget.show()
            self._jupyter_console.current.focus()
        else:
            self._dock_widget.hide()

    def _focus(self):

        self._set_visible(True)
        self._jupyter_console.current.focus()

    def _on_close_event(self, e):

        self._set_visible(False)
