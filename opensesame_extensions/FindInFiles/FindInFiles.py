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
import fnmatch
from qtpy.QtWidgets import QTreeWidgetItem, QApplication, QDockWidget
from qtpy.QtCore import Qt
from libopensesame.oslogging import oslogger
from libqtopensesame.extensions import BaseExtension
from libqtopensesame.widgets.base_widget import BaseWidget
from libqtopensesame.misc.translate import translation_context
_ = translation_context(u'FindInFiles', category=u'extension')


def find_text(needle, haystack, case_sensitive=False):

    """
    desc:
        A generator that yields line numbers for each occurence of the needle
        in the haystack.

    arguments:
        needle:      The text to search for.
        haystack:    The text to search through.

    keywords:
        case_sensitive:     Indicates whether searching should be case
                            sensitive or not.

    returns:
        An iterator of matching line numbers.
    """

    if not case_sensitive:
        needle = needle.lower()
        haystack = haystack.lower()
    start = 0
    end = len(haystack)
    while needle in haystack[start:]:
        pos = haystack.find(needle, start, end)
        if pos < 0:
            break
        yield haystack.count(u'\n', 0, pos) + 1
        start = pos + len(needle)


class FindWidget(BaseWidget):

    def __init__(self, main_window):

        super(FindWidget, self).__init__(
            main_window,
            ui=u'extensions.FindInFiles.find_in_files'
        )
        try:
            self._ide = self.extension_manager['OpenSesameIDE']
        except Exception:
            self.ui.find_in_files.disable()
            self.extension_manager.fire(
                u'notify',
                message=_(u'FindInFiles requires the OpenSesameIDE extension')
            )
            return

        self.ui.button_find.clicked.connect(self._find)
        self.ui.lineedit_needle.returnPressed.connect(self._find)
        self.ui.lineedit_filter.returnPressed.connect(self._find)
        self.ui.button_cancel.clicked.connect(self._cancel)
        self.ui.button_cancel.hide()
        self.ui.treewidget_results.itemActivated.connect(self._open_result)

    def setFocus(self):

        super(FindWidget, self).setFocus()
        self.ui.lineedit_needle.setFocus()

    def _open_result(self, item, column):

        path, line_number = item.result
        self.extension_manager.fire(
            u'ide_open_file',
            path=path,
            line_number=line_number
        )
        self.tabwidget.switch(u'OpenSesameIDE')

    def _find(self):

        needle = self.ui.lineedit_needle.text().strip()
        self._canceled = False
        if not needle:
            return
        filter = self.ui.lineedit_filter.text().strip()
        self.ui.button_cancel.show()
        self.ui.button_find.hide()
        self.ui.treewidget_results.clear()
        for path in list(self._ide.project_files()):
            if self._canceled:
                break
            if filter and not fnmatch.fnmatch(path, filter):
                continue
            haystack = safe_read(path)
            lines = None
            for line_number in find_text(needle, haystack):
                if lines is None:
                    lines = haystack.split(u'\n')
                    path_item = QTreeWidgetItem(
                        self.ui.treewidget_results,
                        [path]
                    )
                    path_item.result = path, 1
                    self.ui.treewidget_results.addTopLevelItem(path_item)
                line_item = QTreeWidgetItem(
                    path_item, [
                        u'{}: {}'.format(
                            line_number, lines[line_number - 1].strip()
                        )
                    ]
                )
                line_item.result = path, line_number
                path_item.addChild(line_item)
            try:
                self.ui.treewidget_results.expandAll()
            except RuntimeError:
                oslogger.debug('closed during search')
                return
            QApplication.processEvents()
        self.ui.button_cancel.hide()
        self.ui.button_find.show()

    def _cancel(self):

        self._canceled = True


class FindDockWidget(QDockWidget):

    def __init__(self, parent):

        super(FindDockWidget, self).__init__(parent)
        self._main_window = parent
        self._find_widget = FindWidget(self._main_window)
        self.setWidget(self._find_widget)
        self.setWindowTitle(_(u'Find in projects'))
        self._find_widget.setFocus()

    def closeEvent(self, e):

        self._main_window.removeDockWidget(self)
        e.accept()


class FindInFiles(BaseExtension):

    def activate(self):

        self.main_window.addDockWidget(
            Qt.RightDockWidgetArea,
            FindDockWidget(self.main_window)
        )
