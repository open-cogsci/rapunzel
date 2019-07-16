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
from libqtopensesame.misc.base_subcomponent import BaseSubcomponent
from qtpy.QtWidgets import QTabWidget
from jupyter_tabwidget.jupyter_console import JupyterConsole
from jupyter_tabwidget.console_cornerwidget import ConsoleCornerWidget


class ConsoleTabWidget(QTabWidget, BaseSubcomponent):

    def __init__(self, parent, kwargs):

        super(ConsoleTabWidget, self).__init__(parent)
        self.setup(parent)
        self.setCornerWidget(ConsoleCornerWidget(self))
        self.tabCloseRequested.connect(self.close)
        self._kwargs = kwargs
        self.add()

    def add(self):

        self.addTab(
            JupyterConsole(self, **self._kwargs),
            self.main_window.theme.qicon('os-debug'),
            u''
        )
        self.setTabsClosable(self.count() > 1)
        self.setCurrentIndex(self.count() - 1)

    def close(self, index):

        console = self.widget(index)
        console.shutdown()
        self.removeTab(index)
        self.setTabsClosable(self.count() > 1)

    def close_all(self):

        while self.count():
            self.close()

    @property
    def current(self):

        return self.currentWidget()
