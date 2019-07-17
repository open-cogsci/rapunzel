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
from libopensesame.oslogging import oslogger
from libqtopensesame.misc.config import cfg
from libqtopensesame.widgets.base_widget import BaseWidget
from qtpy.QtWidgets import QHBoxLayout
from qtpy.QtGui import QFont
from qtconsole import styles
from qtconsole.rich_jupyter_widget import RichJupyterWidget


class JupyterConsole(BaseWidget):

    def __init__(self, parent=None, kernel=u'python3', inprocess=False):

        super(JupyterConsole, self).__init__(parent)
        # Initialize Jupyter Widget
        if inprocess:
            from qtconsole.inprocess import (
                QtInProcessKernelManager as QtKernelManager
            )
        else:
            from qtconsole.manager import QtKernelManager
        self._inprocess = inprocess
        self._kernel_manager = QtKernelManager(kernel_name=kernel)
        self._kernel_manager.start_kernel()
        self._kernel_client = self._kernel_manager.client()
        self._kernel_client.start_channels()
        self._jupyter_widget = RichJupyterWidget()
        self._jupyter_widget.kernel_manager = self._kernel_manager
        self._jupyter_widget.kernel_client = self._kernel_client
        # Set theme
        self._jupyter_widget._control.setFont(
            QFont(
                cfg.pyqode_font_name,
                cfg.pyqode_font_size
            )
        )
        self._jupyter_widget.style_sheet = styles.sheet_from_template(
            cfg.pyqode_color_scheme,
            u'linux' if styles.dark_style(cfg.pyqode_color_scheme) else 'lightbg'
        )
        self._jupyter_widget.syntax_style = cfg.pyqode_color_scheme
        self._jupyter_widget._syntax_style_changed()
        self._jupyter_widget._style_sheet_changed()
        # Add to layout
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(6, 6, 6, 6)
        self._layout.addWidget(self._jupyter_widget)
        self.setLayout(self._layout)

    def capture_stdout(self):

        sys.stdout = self
        sys.stderr = self

    def release_stdout(self):

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def isatty(self):

        return False

    def flush(self):

        pass

    def execute(self, code):

        self._jupyter_widget.execute(code)

    def write(self, msg):

        self._jupyter_widget._control.insertPlainText(
            safe_decode(msg, errors=u'ignore')
        )
        self._jupyter_widget._control.ensureCursorVisible()

    def focus(self):

        self.setFocus()

    def restart(self):

        oslogger.debug(u'restarting kernel')
        self._jupyter_widget.request_restart_kernel()
        self._jupyter_widget.reset(clear=True)

    def interrupt(self):

        oslogger.debug(u'interrupting kernel')
        self._jupyter_widget.request_interrupt_kernel()

    def shutdown(self):

        oslogger.debug(u'shutting down kernel')
        self._jupyter_widget.kernel_client.stop_channels()
        self._jupyter_widget.kernel_manager.shutdown_kernel()

    def show_prompt(self):

        self._jupyter_widget._show_interpreter_prompt()

    def get_globals(self):

        if self._inprocess:
            return self._kernel_manager.kernel.shell.user_global_ns.copy()
        return {}

    def set_globals(self, global_dict):

        if self._inprocess:
            self._kernel_manager.kernel.shell.push(global_dict)
