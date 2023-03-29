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
import re
import multiprocessing
from pathlib import Path
from qtpy.QtWidgets import QTreeWidgetItem, QDockWidget
from qtpy.QtCore import Qt, QTimer
from libopensesame.oslogging import oslogger
from libqtopensesame.extensions import BaseExtension
from libqtopensesame.widgets.base_widget import BaseWidget
from libqtopensesame.misc.translate import translation_context
_ = translation_context(u'FindInFiles', category=u'extension')

MAX_LINE_LENGTH = 80  # Maximum length of lines in search results


def find_text(needle, haystack, case_sensitive=False):
    """A generator that yields line numbers for each occurence of the needle in
    the haystack.

    Parameters
    ----------
    needle : str or re.pattern
        The text or regular expression to search for.
    haystack : str
        The text to search through.
    case_sensitive : bool, optional
        Indicates whether searching should be case sensitive or not.

    Returns
    -------
    iterator of int
        An iterator of matching line numbers.
    """
    if isinstance(needle, re.Pattern):
        for match in re.finditer(needle, haystack):
            line = haystack.count('\n', 0, match.start()) + 1
            yield line
        return
    if not case_sensitive:
        needle = needle.lower()
        haystack = haystack.lower()
    start = 0
    end = len(haystack)
    prev_line = None
    while needle in haystack[start:]:
        pos = haystack.find(needle, start, end)
        if pos < 0:
            break
        line = haystack.count('\n', 0, pos) + 1
        if line != prev_line:
            yield line
        prev_line = line
        start = pos + len(needle)


def find_text_in_files(queue, needle, file_list, filter, case_sensitive=False,
                       regex=False):
    
    if regex:
        if case_sensitive:
            needle = re.compile(needle)
        else:
            needle = re.compile(needle, re.IGNORECASE)
    elif not case_sensitive:
        needle = needle.lower()
    for path in file_list:
        if filter and not fnmatch.fnmatch(path, filter):
            continue
        try:
            haystack = safe_read(path)
        except FileNotFoundError:  # Deleted after file list was built
            continue
        except OSError:
            # FileNotFoundError maps onto IOError, but Py2 gives OSError
            continue
        lines = haystack.splitlines()
        for line_number in find_text(needle, haystack,
                                     case_sensitive=case_sensitive):
            line = lines[line_number - 1]
            if regex:
                span = needle.search(line).span()
                index = span[0]
            else: 
                index = (line.find(needle) if case_sensitive
                         else line.lower().find(needle))
                span = index, index + len(needle)
            if len(line) > MAX_LINE_LENGTH:
                full_length = len(line)
                line = line[index: index + MAX_LINE_LENGTH]
                if index > 0:
                    line = u'(…) ' + line
                if index + MAX_LINE_LENGTH < full_length:
                    line = line + u' (…)'
            queue.put((path, line_number, line, span))
    queue.put((None, None, None, None))


class FindWidget(BaseWidget):

    def __init__(self, main_window):

        super().__init__(main_window,
                         ui='extensions.find_in_files.find_in_files')
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
        self.ui.lineedit_replace.hide()
        self.ui.button_replace.hide()
        self.ui.button_replace.clicked.connect(self._replace)
        self.ui.button_cancel.clicked.connect(self._cancel)
        self.ui.button_cancel.hide()
        self.ui.treewidget_results.itemActivated.connect(self._open_result)
        self._finder = None

    def setFocus(self):

        super(FindWidget, self).setFocus()
        selection = self.extension_manager.provide('ide_current_selection')
        if selection and u'\n' not in selection:
            self.ui.lineedit_needle.setText(selection)
        self.ui.lineedit_needle.setFocus()

    def _open_result(self, item, column):

        path, line_number = item.result
        self.extension_manager.fire(
            u'ide_open_file',
            path=path,
            line_number=line_number
        )
        self.extension_manager.fire(
            u'ide_search_text',
            needle=self.ui.lineedit_needle.text().strip(),
        )
        self.tabwidget.switch(u'OpenSesameIDE')

    def _find(self):

        needle = self.ui.lineedit_needle.text().strip()
        self._canceled = False
        if not needle:
            return
        if self.ui.toolbutton_regex.isChecked():
            try:
                re.compile(needle)
            except re.error:
                self.extension_manager.fire(
                    'notify',
                    message=_('Cannot find text because regular expression is invalid'),
                    category='warning')
                return
        filter = self.ui.lineedit_filter.text().strip()
        self.ui.lineedit_replace.hide()
        self.ui.button_replace.hide()
        self.ui.button_cancel.show()
        self.ui.button_find.hide()
        self.ui.treewidget_results.clear()
        self._last_path = None
        self._results = []
        self._queue = multiprocessing.Queue()
        self._finder = multiprocessing.Process(
            target=find_text_in_files,
            args=(
                self._queue,
                needle,
                list(self._ide.project_files()),
                filter,
                self.ui.toolbutton_match_case.isChecked(),
                self.ui.toolbutton_regex.isChecked()
            )
        )
        self._n_matches = 0
        self._n_files = 0
        self._finder.start()
        oslogger.debug(u'finding {} (PID={})'.format(
            needle,
            self._finder.pid
        ))
        self.extension_manager.fire(
            'register_subprocess',
            pid=self._finder.pid,
            description='find_text_in_files:{}'.format(needle)
        )
        QTimer.singleShot(1000, self._check_finder)
        
    def _check_finder(self):
        
        if self._queue.empty():
            try:
                oslogger.debug(u'no results yet for finder (PID={})'.format(
                        self._finder.pid
                ))
            except ValueError:
                # Is raised when getting the pid of a closed process
                return
            QTimer.singleShot(1000, self._check_finder)
            return
        # The search is finished when the result is all None
        path, line_number, matching_line, span = result = self._queue.get()
        if path is not None:
            self._results.append(result)
        elif not self._canceled:
            self.ui.button_cancel.hide()
            self.ui.button_find.show()
            self._finder.join()
            oslogger.debug(u'finder done (PID={})'.format(self._finder.pid))
            # Show the replace options only if the process terminated
            # successfully and if there were results
            if not self._finder.exitcode and self._results:
                self.ui.lineedit_replace.show()
                self.ui.button_replace.show()
            self._finder.close()
            self.extension_manager.fire(
                u'notify',
                message=_('Found {} match(es) in {} file(s)').format(
                    self._n_matches,
                    self._n_files
                ) if self._n_matches else _('No matches found')
            )
            return
        if path != self._last_path:
            self._path_item = QTreeWidgetItem(
                self.ui.treewidget_results,
                [path]
            )
            self._path_item.result = path, 1
            self.ui.treewidget_results.addTopLevelItem(self._path_item)
            self._last_path = path
            self._n_files += 1
        self._n_matches += 1
        line_item = QTreeWidgetItem(self._path_item,
                                    [f'{line_number}: {matching_line}'])
        line_item.result = path, line_number
        self._path_item.addChild(line_item)
        QTimer.singleShot(10, self._check_finder)
        
    def _replace(self):
        replace_text = self.ui.lineedit_replace.text()
        paths = {}
        for path, line_number, matching_line, span in self._results[::-1]:
            if path not in paths:
                paths[path] = []
            paths[path].append((line_number, span))
        self.extension_manager.fire(
            u'notify',
            message=_('Replacing {} occurrences in {} files').format(
                len(self._results), len(paths)))        
        for path, hits in paths.items():
            path = Path(path)
            content = path.read_text()
            best_newline_count = -1
            for newline in ['\n', '\r', '\r\n']:
                newline_count = content.count(newline)
                if newline_count > best_newline_count:
                    best_newline = newline
                    best_newline_count = newline_count
            lines = content.splitlines()
            for line_number, (from_index, to_index) in hits:
                line_number -= 1  # start from 0
                lines[line_number] = lines[line_number][:from_index] + \
                    replace_text + lines[line_number][to_index:]
            new_content = best_newline.join(lines)
            if content.endswith(newline):
                new_content += newline
            path.write_text(new_content)
        self.ui.lineedit_needle.setText(replace_text)
        self._find()

    def _cancel(self):

        self._canceled = True
        try:
            alive = self._finder is not None and self._finder.is_alive()
        except ValueError:  # process is closed
            return
        if alive:
            oslogger.debug(
                u'terminating finder (PID={})'.format(self._finder.pid)
            )
            self._finder.terminate()


class FindDockWidget(QDockWidget):

    def __init__(self, parent):

        super(FindDockWidget, self).__init__(parent)
        self._main_window = parent
        self._find_widget = FindWidget(self._main_window)
        self.setWidget(self._find_widget)
        self.setWindowTitle(_(u'Find in projects'))
        self.setObjectName('FindDockWidget')
        self._find_widget.setFocus()

    def closeEvent(self, e):

        self._main_window.removeDockWidget(self)
        e.accept()
        self._find_widget._cancel()


class FindInFiles(BaseExtension):

    def activate(self):

        self.main_window.addDockWidget(
            Qt.RightDockWidgetArea,
            FindDockWidget(self.main_window)
        )
