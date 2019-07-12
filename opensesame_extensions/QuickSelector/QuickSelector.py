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
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QDialog,
    QLineEdit,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem
)
from libqtopensesame.extensions import BaseExtension
from libqtopensesame.misc.translate import translation_context
from libqtopensesame.misc.config import cfg
_ = translation_context(u'QuickSelector', category=u'extension')


class SearchBox(QLineEdit):

    def keyPressEvent(self, e):

        if e.key() == Qt.Key_Down:
            self.parent().focus_result_box()
            return
        if e.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.parent().select_top_result()
            return
        super(SearchBox, self).keyPressEvent(e)


class ResultBox(QListWidget):

    def keyPressEvent(self, e):

        if (
            (e.key() == Qt.Key_Up and not self.currentRow()) or
            e.key() not in (
                Qt.Key_Down,
                Qt.Key_Up,
                Qt.Key_Return,
                Qt.Key_Enter
            )
        ):
            self.parent().focus_search_box(e)
            return
        super(ResultBox, self).keyPressEvent(e)


class QuickSelectorDialog(QDialog):

    def __init__(self, parent, haystack):

        super(QuickSelectorDialog, self).__init__(
            parent,
            Qt.FramelessWindowHint
        )
        self.setWindowTitle(u'Open file')
        self._haystack = haystack
        self._search_box = SearchBox(self)
        self._search_box.textEdited.connect(self._search)
        self._result_box = ResultBox(self)
        self._result_box.itemActivated.connect(self._select)
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(self._search_box)
        self._layout.addWidget(self._result_box)
        self.setMinimumWidth(cfg.quick_selector_min_width)
        self._search(u'')

    def focus_result_box(self):

        self._result_box.setFocus()
        self._result_box.setCurrentRow(0)

    def focus_search_box(self, e):

        self._search_box.setFocus()
        self._search_box.keyPressEvent(e)

    def select_top_result(self):

        self._select(self._result_box.takeItem(0))

    def _search(self, needle):

        needle = needle.lower()
        self._result_box.show()
        self._result_box.clear()
        for label, data, on_select in self._haystack:
            if not needle or needle in label.lower():
                item = QListWidgetItem(label, self._result_box)
                item.data = data
                item.on_select = on_select
                self._result_box.addItem(item)

    def _select(self, item):

        item.on_select(item.data)
        self.accept()


class QuickSelector(BaseExtension):

    def event_quick_select(self, haystack):

        QuickSelectorDialog(self.main_window, haystack).exec()
