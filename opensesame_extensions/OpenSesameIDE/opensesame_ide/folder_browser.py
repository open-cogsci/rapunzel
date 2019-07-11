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
from pyqode.core.widgets import (
    FileSystemTreeView,
    FileSystemContextMenu
)
from qtpy.QtWidgets import QDockWidget
from libopensesame.oslogging import oslogger
from libqtopensesame.misc.translate import translation_context
_ = translation_context(u'OpenSesameIDE', category=u'extension')


class FolderBrowserDockWidget(QDockWidget):

    def __init__(self, parent, ide, path):

        super(FolderBrowserDockWidget, self).__init__(parent)
        self.main_window = parent
        self._ide = ide
        self.path = path
        self._folder_browser = FolderBrowser(parent, ide, path)
        self.setWidget(self._folder_browser)
        self.setFeatures(
            QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable
        )
        self.visibilityChanged.connect(self.on_visibility_changed)

    def on_visibility_changed(self, visible):

        if not visible:
            self.visibilityChanged.disconnect()
            self._ide.remove_folder_browser_dock_widget(self)


class FolderBrowser(FileSystemTreeView):

    def __init__(self, parent, ide, path):

        super(FolderBrowser, self).__init__(parent)
        self.main_window = parent
        self._path = path
        self._ide = ide
        self.set_root_path(path)
        self.set_context_menu(FileSystemContextMenu())

    def mouseDoubleClickEvent(self, event):

        path = self.fileInfo(self.indexAt(event.pos())).filePath()
        self.open_file(path)

    def open_file(self, path):

        if not os.path.exists(path) or os.path.isdir(path):
            return
        self._ide.open_document(path)

    def list_files(self):

        return self.helper._get_files(self._path)
