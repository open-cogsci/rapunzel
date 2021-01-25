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
import sys
import mimetypes
import textwrap
import inspect
from libopensesame import metadata
from libopensesame.oslogging import oslogger
from libqtopensesame.extensions import BaseExtension
from libqtopensesame.misc.config import cfg
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import QFileDialog, QMessageBox, QPushButton, QApplication
from opensesame_ide import FolderBrowserDockWidget, MenuBar
from libqtopensesame.misc.translate import translation_context
from pyqode.core import widgets
from pyqode.core.api.utils import TextHelper
from pyqode_extras.widgets import FallbackCodeEdit
_ = translation_context(u'OpenSesameIDE', category=u'extension')


def with_editor_and_cursor(fnc):
    
    def inner(self, *args, **kwargs):
        
        editor = self._current_editor()
        if editor is None:
            return
        if takes_args:
            return fnc(self, editor, editor.textCursor(), *args, **kwargs)
        return fnc(self, editor, editor.textCursor())
    
    takes_args = len(inspect.getargspec(fnc).args) > 3
    return inner


def with_editor(fnc):
    
    def inner(self, *args, **kwargs):
        
        editor = self._current_editor()
        if editor is None:
            return
        if takes_args:
            return fnc(self, editor, *args, **kwargs)
        return fnc(self, editor)
    
    takes_args = len(inspect.getargspec(fnc).args) > 2
    return inner


class OpenSesameIDE(BaseExtension):
    
    preferences_ui = 'extensions.OpenSesameIDE.preferences'

    def event_startup(self):

        if self.main_window.mode != u'ide':
            return
        metadata.identity = 'Rapunzel {}'.format(self.info['version'])
        os.path.splitunc = lambda path: ('', path)  # Backwards compatibility
        self._register_mimetypes()
        self._patch_behavior()
        self._scetw = widgets.SplittableCodeEditTabWidget(self.main_window)
        self._scetw.main_tab_widget.cornerWidget().hide()
        self._scetw.fallback_editor = FallbackCodeEdit
        self._scetw.tab_name = u'OpenSesameIDE'
        self._scetw.main_tab_widget.tab_closed.connect(self._on_editor_close)
        self._scetw.tab_bar_visible = cfg.opensesame_ide_show_tab_bar
        self._add_ide_tab()
        self._dock_widgets = {}
        self._set_ignore_patterns()
        self._restore_open_folders()
        self._parse_command_line()
        self._cells_to_run_queue = []
        self.main_window.setWindowTitle(u'Rapunzel')
        self.main_window.setWindowIcon(
            self.theme.qicon(u'rapunzel')
        )
        
    @property
    def dock_widgets(self):
        
        # Turn it into a list so that we don't get race conditions when the
        # dict changes during an iteration
        return list(self._dock_widgets.values())

    def event_setting_changed(self, setting, value):
        
        self.extension_manager.suspend()
        self._menubar.setting_changed(setting, value)
        self.extension_manager.resume()

    def event_ide_open_file(self, path, line_number=1):

        self.open_document(path)
        self.extension_manager.fire('ide_jump_to_line', lineno=line_number)
        
    def event_ide_search_text(self, needle):
        
        editor = self._current_editor()
        if editor is None:
            return u''
        try:
            search_panel = editor.panels.get('SearchAndReplacePanel')
        except KeyError:
            return  # Panel is not installed
        cursor = editor.textCursor()
        needle_pos = cursor.block().text().find(needle)
        if needle_pos < 0:
            needle_pos = editor.toPlainText().find(needle)
        if needle_pos < 0:
            oslogger.warning('failed to find needle in text')
            return
        cursor.clearSelection()
        cursor.movePosition(cursor.StartOfBlock, cursor.MoveAnchor)
        cursor.movePosition(
            cursor.NextCharacter,
            cursor.MoveAnchor,
            needle_pos
        )
        cursor.movePosition(
            cursor.NextCharacter,
            cursor.KeepAnchor,
            len(needle)
        )
        editor.setTextCursor(cursor)
        search_panel.on_search()

    def event_ide_show_tab_bar(self, show_tab_bar):

        cfg.opensesame_ide_show_tab_bar = show_tab_bar
        self._scetw.tab_bar_visible = show_tab_bar

    def event_ide_new_file(self, source=None, ext=None):

        self.new_file(ext=ext)
        if source is None:
            return
        self._current_editor().setPlainText(source)

    def event_ide_run_current_file(self):

        self.run_current_file()

    def event_ide_run_current_selection(self):

        self.run_current_selection()
        
    def provide_ide_project_folders(self):
        
        return [d.path for d in self.dock_widgets]

    def provide_ide_current_editor(self):

        return self._current_editor()
    
    def provide_ide_editors(self):

        return self._scetw.widgets()
        
    def provide_ide_current_source(self):

        editor = self._current_editor()
        if editor is None:
            return u''
        return editor.toPlainText()
        
    def provide_current_path(self):
        
        editor = self._current_editor()
        if editor is None:
            return u''
        return editor.file.path
        
    def provide_ide_current_selection(self):
        
        editor = self._current_editor()
        if editor is None:
            return u''
        cursor = editor.textCursor()
        if not cursor.hasSelection():
            return u''
        return cursor.selectedText().replace(u'\u2029', u'\n')

    def provide_ide_current_word(self):
        
        editor = self._current_editor()
        if editor is None:
            return u''
        return TextHelper(editor).word_under_cursor(
            select_whole_word=True
        ).selectedText()
        
    def toggle_breakpoint(self):

        editor = self._current_editor()
        if editor is None or 'BreakpointMode' not in editor.modes.keys():
            return
        editor.modes.get('BreakpointMode').toggle_breakpoint()

    def provide_ide_current_language(self):

        editor = self._current_editor()
        if editor is None:
            return None
        try:
            return editor.language
        except AttributeError:
            # In rare cases, the editor may not have a language property, or 
            # the property may crash, both of which result in an 
            # AttributeError.
            pass

    def open_document(self, path):

        # First normalize the path and check if there's a custom handler for it
        path = os.path.abspath(os.path.normpath(path))
        ext = os.path.splitext(path)[1].lstrip('.').lower()
        handler = self.extension_manager.provide(
            'open_file_extension_{}'.format(ext)
        )
        if not handler:
            self._open_document_as_text(path)
            return
        oslogger.debug('custom handler for .{} extension'.format(ext))
        handler_fnc, handler_desc = handler
        self.extension_manager.fire(
            u'quick_select',
            haystack=[
                (handler_desc, path, handler_fnc),
                (_('Open as text'), path, self._open_document_as_text)
            ],
            placeholder_text=_(u'How do you want to open this file?')
        )
        
    def _open_document_as_text(self, path):
        
        # If the file is already open, switch to it
        for editor in self._scetw.widgets():
            if editor.file.path is None:
                continue
            if path == os.path.abspath(os.path.normpath(editor.file.path)):
                editor.parent().parent().setCurrentWidget(editor)
                editor.setFocus()
                return
        # Don't try to open non-existing paths
        if not os.path.isfile(path):
            self.extension_manager.fire(
                u'notify',
                message=_(u'{} is not a file'.format(path)),
                category=u'warning'
            )
            return
        # Otherwise open it in a new tab in the current splitter
        editor = self._current_splitter().open_document(
            path,
            encoding=self._default_encoding,
            replace_tabs_by_spaces=cfg.opensesame_ide_auto_tabs_to_spaces,
            clean_trailing_whitespaces=cfg.opensesame_ide_strip_lines,
            show_whitespaces=None
        )
        self.extension_manager.fire(
            u'register_editor',
            editor=editor
        )

    def remove_folder_browser_dock_widget(self, dock_widget):

        oslogger.debug(u'removing folder browser: {}'.format(dock_widget.path))
        self.main_window.removeDockWidget(dock_widget)
        del self._dock_widgets[dock_widget.path]
        self._remember_open_folders()

    def close_tab(self):

        self.extension_manager.fire('pyqode_suspend_auto_backend_restart')
        tab_widget = self._current_tabwidget()
        if tab_widget is not None:
            tab_widget.close()
        self.extension_manager.fire('pyqode_resume_auto_backend_restart')

    def close_all_tabs(self):

        self.extension_manager.fire('pyqode_suspend_auto_backend_restart')
        tab_widget = self._current_tabwidget()
        if tab_widget is not None:
            tab_widget.close_all()
        self.extension_manager.fire('pyqode_resume_auto_backend_restart')

    def close_other_tabs(self):

        self.extension_manager.fire('pyqode_suspend_auto_backend_restart')
        tab_widget = self._current_tabwidget()
        if tab_widget is not None:
            tab_widget.close_others()
        self.extension_manager.fire('pyqode_resume_auto_backend_restart')

    def switch_tab_next(self):

        self._switch_tab(1)

    def switch_splitter_previous(self):

        self._switch_splitter(-1)

    def switch_splitter_next(self):

        self._switch_splitter(1)

    def switch_tab_previous(self):

        self._switch_tab(-1)

    def split_horizontal(self):

        self._split(Qt.Horizontal)

    def split_vertical(self):

        self._split(Qt.Vertical)

    def select_and_open_folder(self, *args):

        path = QFileDialog.getExistingDirectory(
            self.main_window,
            directory=cfg.file_dialog_path
        )
        if isinstance(path, tuple):
            path = path[0]
        if not path:
            return
        cfg.file_dialog_path = path
        self._open_folder(path)
        self._add_recent_folder(path)
        self._remember_open_folders()

    def new_file(self, ext=None):

        if not ext:
            ext = cfg.opensesame_ide_default_extension
        editor = self._current_splitter().create_new_document(extension=ext)
        self.extension_manager.fire(
            u'register_editor',
            editor=editor
        )

    def save_file(self):

        editor = self._current_original_editor()
        if not editor:
            return
        # PyQode gives a very confusing error message when an encoding error
        # during saving. So here we catch that and give the user the chance to
        # select a different encoding when this happens.
        try:
            editor.toPlainText().encode(editor.file.encoding)
        except UnicodeEncodeError:
            self.extension_manager.fire(
                'notify',
                message=_('Cannot save file with this encoding'),
                category='warning',
                always_show=True
            )
            return
        if not editor.file.path:
            self.save_file_as()
        else:
            self._scetw.save_current()
        self.extension_manager.fire('ide_save_current_file')

    def save_file_as(self):

        editor = self._current_editor()
        from_path = editor.file.path if editor else ''
        self._current_splitter().save_current_as()
        editor = self._current_editor()
        if editor is None:
            return
        path = editor.file.path
        if not path:
            return
        mimetype, encoding = mimetypes.guess_type(path)
        if mimetype in editor.mimetypes:
            return
        self.close_tab()
        self.open_document(path)
        self.extension_manager.fire(
            'ide_save_current_file_as',
            from_path=from_path,
            to_path=path
        )

    def open_file(self, *args):

        path = QFileDialog.getOpenFileName(
            self.main_window,
            _(u"Open file"),
            directory=cfg.file_dialog_path
        )
        if isinstance(path, tuple):
            path = path[0]
        if not path:
            return
        cfg.file_dialog_path = os.path.dirname(path)
        self.open_document(path)
        # And remember the folder
        self._add_recent_folder(os.path.dirname(path))

    def folder_browsers_visible(self):

        return all(
            dockwidget.isVisible()
            for dockwidget in self.dock_widgets
        )

    def toggle_folder_browsers(self):

        hidden = not self.folder_browsers_visible()
        oslogger.debug(
            'setting folder-browser visibility to {}'.format(hidden)
        )
        for dockwidget in self.dock_widgets:
            dockwidget.setVisible(hidden)

    def _select_logical_line(self, editor, scan_width=8):

        best_cursor = None
        smallest_chunk = float('inf')
        for n_up in range(scan_width):
            for n_down in range(scan_width):
                if best_cursor is not None and n_up + n_down >= smallest_chunk:
                    continue
                cursor = editor.textCursor()
                cursor.movePosition(cursor.StartOfLine)
                cursor.movePosition(cursor.Up, n=n_up)
                cursor.movePosition(
                    cursor.Down,
                    cursor.KeepAnchor,
                    n=n_up + n_down
                )
                cursor.movePosition(cursor.EndOfLine, cursor.KeepAnchor)
                if not best_cursor:
                    best_cursor = cursor
                code = cursor.selectedText().replace(u'\u2029', u'\n')
                if not self.extension_manager.provide(
                    'jupyter_check_syntax',
                    code=code
                ):
                    continue
                best_cursor = cursor
                smallest_chunk = n_up + n_down
        return best_cursor

    def _run_notify(self, msg):

        self.extension_manager.fire(
            u'notify',
            message=msg,
            timeout=1000,
            always_show=True
        )

    def _run_project_file(self, project_file):

        if u'kernel' in project_file:
            self.extension_manager.fire(
                u'jupyter_start_kernel',
                kernel=project_file['kernel']
            )
        self.extension_manager.fire(
            u'jupyter_run_code',
            code=project_file.get(u'run', u'')
        )
        return

    def run_current_file(self, debug=False):

        editor = self._current_editor()
        if editor is None:
            return
        if editor.dirty:
            if not cfg.opensesame_ide_run_autosave:
                retval = self._save_and_run_dialog()
                if retval == 2:  # Cancel
                    return
                if retval == 1:  # Save and run
                    cfg.opensesame_ide_run_autosave = True
            self.save_file()
        if not debug:
            project_file = self._current_project_file()
            if project_file:
                self._run_notify(_(u'Running project'))
                self._run_project_file(project_file)
                return
        if (
            editor is None or
            not os.path.exists(editor.file.path)
        ):
            return
        self._run_notify(_(u'Running file'))
        self.extension_manager.fire(
            u'jupyter_run_file',
            path=editor.file.path,
            debug=debug
        )
        
    def run_debug(self):
        
        self.run_current_file(debug=True)
        
    def clear_breakpoints(self):
        
        self.extension_manager.fire('pyqode_clear_breakpoints')

    def change_working_directory(self):

        path = self._current_path()
        if not os.path.isfile(path):
            return
        self.extension_manager.fire(
            u'jupyter_change_dir',
            path=os.path.dirname(path)
        )
    
    @with_editor_and_cursor
    def run_from_current_position(self, editor, cursor):
        
        self._run_range(
            editor,
            cursor,
            cursor.position(),
            editor.document().characterCount() - 1
        )
    
    @with_editor_and_cursor
    def run_up_to_current_position(self, editor, cursor):
        
        self._run_range(editor, cursor, 0, cursor.position())

    def _run_range(self, editor, cursor, from_pos, end_pos):
        """Runs either a selection of cells in a certain range, or a selection
        of lines if no cells are defined.
        """

        # If the current editor is attached to a file, change the working
        # directory if this behavior is specified in the configuration
        if cfg.opensesame_ide_run_selection_change_working_directory:
            self.change_working_directory()
        cells = self.extension_manager.provide(
            u'jupyter_notebook_cells',
            code=editor.toPlainText(),
            cell_types=[u'code']
        )
        if not cells:
            cursor.setPosition(from_pos)
            cursor.movePosition(cursor.StartOfBlock, cursor.MoveAnchor)
            cursor.setPosition(end_pos, cursor.KeepAnchor)
            cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
            editor.setTextCursor(cursor)
            self._run_notify(_(u'Running code range'))
            self.extension_manager.fire(
                u'jupyter_run_code',
                code=self._selected_text(cursor)
            )
            return
        self._run_notify(_(u'Running multiple notebook cells'))
        self._cells_to_run_queue = [
            (cell_number, editor) for cell_number, cell in enumerate(cells)
            if cell['start'] <= end_pos and cell['end'] >= from_pos
        ]
        self._run_cell_from_queue()
        
    def event_jupyter_execute_finished(self):
        """If the jupyter kernel is done, execute the next queued cell."""
        if self._cells_to_run_queue:
            QTimer.singleShot(1000, self._run_cell_from_queue)
        
    def _run_cell_from_queue(self):
        """Checks if there are cells cued to be executed. If so, then the cell
        is retrieved by number, and not by position, because the cell positions
        may have changed since the cell was queued.
        """
        if not self._cells_to_run_queue:
            oslogger.debug('no more cells queued')
            return
        # In certain race conditions, the kernel may already be active again
        # before we've had a chance to execute this cell. If so, try again
        # later.
        if self.extension_manager.provide('jupyter_kernel_running'):
            oslogger.debug('kernel running, trying again later')
            QTimer.singleShot(1000, self._run_cell_from_queue)
            return
        # Image annotations removes the hourglass from the document only a
        # little while after the executing is stopped. If we then start a new
        # execution, this will confuse things. So we wait until capturing is
        # completely done.
        if self.extension_manager.provide('image_annotations_capturing'):
            oslogger.debug('still capturing, trying again later')
            QTimer.singleShot(1000, self._run_cell_from_queue)
            return
        cell_number, editor = self._cells_to_run_queue.pop(0)
        oslogger.debug('running cell {}'.format(cell_number))
        cells = self.extension_manager.provide(
            u'jupyter_notebook_cells',
            code=editor.toPlainText(),
            cell_types=[u'code']
        )
        try:
            cell = cells[cell_number]
        except IndexError:
            # Something changed in the code such that the cell number doesn't
            # exist anymore.
            return
        cursor = editor.textCursor()
        cursor.setPosition(cell['start'])
        cursor.setPosition(cell['end'], cursor.KeepAnchor)
        editor.setTextCursor(cursor)
        self.extension_manager.fire(
            u'jupyter_run_code',
            code=self._selected_text(cursor),
            editor=editor
        )
    
    @with_editor_and_cursor
    def run_current_selection(self, editor, cursor):

        # If the current editor is attached to a file, change the working
        # directory if this behavior is specified in the configuration
        if cfg.opensesame_ide_run_selection_change_working_directory:
            self.change_working_directory()
        if not cursor.hasSelection():
            cells = self.extension_manager.provide(
                u'jupyter_notebook_cells',
                code=editor.toPlainText(),
                cell_types=[u'code']
            )
            if cells is None:
                cells = []
            # Loop through the cells from the bottom up and run the first cell
            # that starts above the cursor.
            for cell in cells[::-1]:
                if cursor.position() >= cell['start']:
                    cursor.setPosition(cell['start'])
                    cursor.setPosition(cell['end'], cursor.KeepAnchor)
                    self._run_notify(_(u'Running notebook cell'))
                    break
            else:
                # Select current line
                # cursor.movePosition(cursor.StartOfLine)
                # cursor.movePosition(cursor.EndOfLine, cursor.KeepAnchor)
                cursor = self._select_logical_line(editor)
                self._run_notify(_(u'Running current line'))
            editor.setTextCursor(cursor)
        else:
            self._run_notify(_(u'Running selection'))
        self.extension_manager.fire(
            u'jupyter_run_code',
            code=self._selected_text(cursor)
        )

    def run_interrupt(self):

        self.extension_manager.fire(u'jupyter_interrupt')
        self._cells_to_run_queue = []

    def run_restart(self):

        self.extension_manager.fire(u'jupyter_restart')
        self._cells_to_run_queue = []

    def open_plugin_manager(self):

        self.extension_manager.activate(u'plugin_manager')

    @with_editor_and_cursor
    def event_ide_jump_to_line(self, editor, cursor, lineno):

        lines = editor.toPlainText().split(u'\n')
        position = sum([len(line) for line in lines[:lineno - 1]]) + lineno - 1
        cursor.setPosition(position)
        editor.setTextCursor(cursor)

    def quick_select_files(self):

        haystack = []
        for dock_widget in self.dock_widgets:
            strip_first = len(os.path.split(dock_widget.path)[0])
            for path in dock_widget.file_list:
                label = path[strip_first + 1:]
                data = path
                haystack.append((label, data, self.open_document))
        self.extension_manager.fire(
            u'quick_select',
            haystack=haystack,
            placeholder_text=_(u'Search project files or browse disk …'),
            default=(_(u'Browse disk …'), None, self.open_file)
        )

    def quick_select_folders(self):

        haystack = []
        norm_paths = {
            os.path.abspath(os.path.normpath(path))
            for path in cfg.opensesame_ide_recent_folders.split(u';')
            if os.path.isdir(path)
        }
        for path in sorted(norm_paths):
            haystack.append((path, path, self._open_folder))
        self.extension_manager.fire(
            u'quick_select',
            haystack=haystack,
            placeholder_text=_(u'Search recent folders or browse disk …'),
            default=(_(u'Browse disk …'), None, self.select_and_open_folder)
        )

    def project_files(self, extra_ignore_pattern=None):

        for dock_widget in self.dock_widgets:
            for path in dock_widget.file_list:
                yield path
                
    def settings_widget(self):
        
        from opensesame_ide import Preferences
        return Preferences(self.main_window)
        
    @with_editor
    def _split(self, editor, direction):

        splitter = self._current_splitter()
        # If there are no child splitters, we use the regular split() method
        if not splitter.child_splitters:
            subsplitter = splitter.split(editor, direction)
            subsplitter.main_tab_widget.tab_closed.connect(
                self._on_editor_close
            )
            self.extension_manager.fire(
                u'register_editor',
                editor=self._current_editor()
            )
            return
        # If there are child splitters, then we use a double split to put the
        # current editor inside a new splitter with a clone of itself. The
        # original editor is then closed, and all other tabs are moved into the
        # new splitter. This is an ugly hack to deal with a limitation in
        # pyqode.
        self.main_window.setUpdatesEnabled(False)
        subsplitter = splitter.split(editor, splitter.orientation(), index=1)
        subsplitter.main_tab_widget.tab_closed.connect(self._on_editor_close)
        editor = self._current_editor()
        self.extension_manager.fire(
            u'register_editor',
            editor=editor
        )
        subsubsplitter = subsplitter.split(editor, direction, index=1)
        subsubsplitter.main_tab_widget.tab_closed.connect(
            self._on_editor_close
        )
        editor = self._current_editor()
        self.extension_manager.fire(
            u'register_editor',
            editor=editor
        )
        # Close the editor in the original splitter
        splitter.main_tab_widget.close()
        # Copy the remaining editors of the original splitter to the
        # subsplitter
        editors = [
            (index, splitter.main_tab_widget.widget(index))
            for index in range(splitter.main_tab_widget.count())
        ]
        for index, editor in editors[::-1]:
            subsplitter.main_tab_widget._on_tab_move_request(editor, 0)
        subsplitter.main_tab_widget.setCurrentIndex(
            subsplitter.main_tab_widget.count() - 1
        )
        # Set the focus to the editor in the subsubsplitter
        subsubsplitter.main_tab_widget.widget(0).setFocus()
        self.main_window.setUpdatesEnabled(True)

    def _open_folder(self, path):

        path = os.path.abspath(path)
        if path in list(self._dock_widgets):
            return
        oslogger.debug(u'adding folder browser: {}'.format(path))
        dock_widget = FolderBrowserDockWidget(self.main_window, self, path)
        self.main_window.addDockWidget(
            Qt.LeftDockWidgetArea,
            dock_widget
        )
        self._dock_widgets[path] = dock_widget
        if not self.folder_browsers_visible():
            self.toggle_folder_browsers()
        self._remember_open_folders()
        self._add_recent_folder(path)

    def close_all_folders(self):

        for dockwidget in self.dock_widgets:
            dockwidget.close()

    @with_editor
    def locate_file_in_folder(self, editor):

        for dockwidget in self.dock_widgets:
            dockwidget.setVisible(True)
        for dock_widget in self.dock_widgets:
            dock_widget.select_path(editor.file.path)
        if not self.folder_browsers_visible():
            self.toggle_folder_browsers()

    def _patch_close_event(self, fnc):

        def inner(e):

            self.main_window.setUpdatesEnabled(False)
            self.extension_manager.fire('pyqode_suspend_auto_backend_restart')
            self._scetw.closeEvent(e)
            self.extension_manager.fire('pyqode_resume_auto_backend_restart')
            self.main_window.setUpdatesEnabled(True)
            if e.isAccepted():
                fnc(e)

        return inner

    def _patch_show_event(self, fnc):

        def inner(e):

            fnc(e)
            self._menubar._action_toggle_folder_browsers.setChecked(
                self.folder_browsers_visible()
            )

        return inner

    def _patch_behavior(self):

        # We open the IDE in a tab, and then set one-tab mode so that there
        # aren't two layers of tabs. When another tab (say preferences) is
        # opened, we disable one-tab mode, and then re-enable it again when
        # the IDE tab is the only tab,
        self.tabwidget.switch(u'OpenSesameIDE')
        if not self.main_window.ui.action_onetabmode.isChecked():
            self.main_window.ui.action_onetabmode.trigger()
        self.tabwidget.add = self._patch_tabwidget_add(self.tabwidget.add)
        self.tabwidget.tab_removed.connect(self._on_tabwidget_close)
        self.tabwidget.shortcut_switch_left.setKey(u'')
        self.tabwidget.shortcut_switch_right.setKey(u'')
        # Create a custom menubar
        self._menubar = MenuBar(self.main_window, self)
        self.extension_manager.fire(
            'ide_menubar_initialized',
            menubar=self._menubar
        )
        self.main_window.setMenuBar(self._menubar)
        self._toolbar = self._menubar.build_tool_bar()
        self.extension_manager.fire(
            'ide_toolbar_initialized',
            menubar=self._toolbar
        )
        self.main_window.addToolBar(self._toolbar)
        # Patch the starting and closing of the app
        self.main_window.restore_window_state = \
            self._patch_restore_window_state(
                self.main_window.restore_window_state
            )
        self.main_window.closeEvent = self._patch_close_event(
            self.main_window.closeEvent
        )
        self.main_window.showEvent = self._patch_show_event(
            self.main_window.showEvent
        )
        # Disable keyboard shortcuts that show the overview area etc.
        self.main_window.ui.shortcut_itemtree.disconnect()
        self.main_window.ui.shortcut_pool.disconnect()

    def _patch_tabwidget_add(self, fnc):

        def inner(widget, *args, **kwargs):

            # We automatically enable one-tab mode if only the rapunzel tab is
            # shown, so that we don't have two layers of tabs.
            if (
                self.tabwidget.count() == 1 and
                self.main_window.ui.action_onetabmode.isChecked()
            ):
                self.main_window.ui.action_onetabmode.trigger()
            # The runner options are not applicable to rapunzel, so we hide
            # those from the preferences tab.
            if (
                hasattr(widget, 'tab_name') and
                widget.tab_name == '__preferences__'
            ):
                widget.ui.groupbox_runner.hide()
            return fnc(widget, *args, **kwargs)

        return inner

    def _on_tabwidget_close(self, index):

        if self.tabwidget.get_widget(u'OpenSesameIDE') is None:
            self._add_ide_tab()
        if self.tabwidget.count() > 1:
            return
        if not self.main_window.ui.action_onetabmode.isChecked():
            self.main_window.ui.action_onetabmode.trigger()

    def _on_editor_close(self, editor):

        self.extension_manager.fire('unregister_editor', editor=editor)

    def _add_ide_tab(self):

        self.tabwidget.add(
            self._scetw,
            u'accessories-text-editor',
            'Rapunzel'
        )

    def _patch_restore_window_state(self, fnc):

        def inner():

            fnc()
            # Remove unused dockwidgets and toolbars
            self.main_window.removeDockWidget(self.main_window.ui.dock_pool)
            self.main_window.removeDockWidget(
                self.main_window.ui.dock_overview
            )
            self.main_window.removeToolBar(self.main_window.ui.toolbar_items)
            self.main_window.removeToolBar(self.main_window.ui.toolbar_main)
            # Always start with the folder browsers visible. This avoids
            # inconsistencies in their visibility.
            for dockwidget in self.dock_widgets:
                dockwidget.setVisible(True)

        return inner

    def _set_ignore_patterns(self):

        self.ignore_patterns = [
            p.strip()
            for p in cfg.opensesame_ide_ignore_patterns.split(u',')
        ]

    def _add_recent_folder(self, path):

        folders = cfg.opensesame_ide_recent_folders.split(u';')
        if path not in folders:
            folders.append(path)
        cfg.opensesame_ide_recent_folders = u';'.join(folders)

    def _remember_open_folders(self):

        folders = [d.path for d in self.dock_widgets]
        cfg.opensesame_ide_last_folder = u';'.join(folders)
        self.extension_manager.fire(
            'ide_project_folders_changed',
            folders=folders
        )

    def _restore_open_folders(self):

        folders = [
            folder
            for folder in cfg.opensesame_ide_last_folder.split(u';')
            if os.path.isdir(folder)
        ]
        if not folders:
            folders = [os.getcwd()]
        for folder in folders:
            self._open_folder(folder)
    
    @BaseExtension.as_thread(wait=750)
    def _open_from_command_line(self, path):

        """This function is run with a timer so that the other extensions have
        a chance to initialize first.
        """

        if os.path.isfile(path):
            self.open_document(path)
        elif os.path.isdir(path):
            self._open_folder(path)

    def _parse_command_line(self):

        for arg in sys.argv[1:]:
            if os.path.exists(arg):
                self._open_from_command_line(arg)

    @with_editor
    def _current_project_file(self, editor):

        for d in self.dock_widgets:
            if not editor.file.path.startswith(d.path):
                continue
            project_file_path = os.path.join(
                d.path,
                cfg.opensesame_ide_project_file
            )
            if not os.path.exists(project_file_path):
                continue
            with open(project_file_path) as fd:
                try:
                    return safe_yaml_load(fd)
                except Exception as e:
                    self.extension_manager.fire(
                        u'notify',
                        message=_(
                            u'Failed to parse project file. '
                            u'See console for details'
                        )
                    )
                    self.console.write(e)

    def _current_editor(self):

        # The current_widget() method of pyqode doesn't always return the
        # correct editor. It appears to be more robust to get the current
        # splitter and then from there get the current widget.
        return self._current_splitter().main_tab_widget.currentWidget()

    @with_editor
    def _current_original_editor(self, editor):

        if editor.original:
            return editor.original
        return editor

    def _current_path(self):

        editor = self._current_original_editor()
        if editor is None:
            return None
        return editor.file.path

    def provide_ide_current_path(self):

        return self._current_path()

    @with_editor
    def _current_tabwidget(self, editor):

        if editor.parent() is None:
            return
        return editor.parent().parent()

    def _current_splitter(self):

        editor = self._scetw.current_widget()
        if editor is None or editor.parent() is None:
            return self._scetw
        return editor.parent().parent().parent()

    def _switch_splitter(self, d):

        if not self._scetw.child_splitters:
            return
        current_splitter = self._current_splitter()
        splitters = self._get_splitters()
        current_splitter_index = splitters.index(current_splitter)
        new_splitter_index = (current_splitter_index + d) % len(splitters)
        new_splitter = splitters[new_splitter_index]
        if new_splitter.main_tab_widget.currentWidget() is not None:
            new_splitter.main_tab_widget.currentWidget().setFocus()
            return
        # If the next splitter is empty, skip it
        if d < 0:
            self._switch_splitter(d - 1)
        else:
            self._switch_splitter(d + 1)

    def _get_splitters(self):

        return self._scetw.get_all_splitters()

    def _switch_tab(self, direction):

        tabwidget = self._current_tabwidget()
        if tabwidget is None:
            return
        tabwidget.setCurrentIndex(
            (tabwidget.currentIndex() + direction) % tabwidget.count()
        )

    def _save_and_run_dialog(self):

        mb = QMessageBox(self.main_window)
        mb.setWindowTitle(_(u'Unsaved changes'))
        mb.setText(
            u'You have unsaved changes. What do you want to do?'
        )
        mb.addButton(
            QPushButton(
                self.theme.qicon(u'os-run'),
                _(u'Save and run')
            ),
            QMessageBox.AcceptRole
        )
        mb.addButton(
            QPushButton(
                self.theme.qicon(u'os-run'),
                _(u'Save, run, and don\'t ask again')
            ),
            QMessageBox.AcceptRole
        )

        mb.addButton(
            QPushButton(
                self.theme.qicon(u'dialog-cancel'),
                _(u'Cancel')
            ),
            QMessageBox.AcceptRole
        )
        return mb.exec_()

    def _toggle_fullscreen(self):

        self.main_window.setWindowState(
            (self.main_window.windowState() & ~Qt.WindowFullScreen)
            if self.main_window.isFullScreen()
            else (self.main_window.windowState() | Qt.WindowFullScreen)
        )

    def _register_mimetypes(self):

        try:
            custom_mimetypes = safe_yaml_load(cfg.opensesame_ide_mimetypes)
            assert(isinstance(custom_mimetypes, dict))
        except Exception:
            oslogger.warning('failed to parse mimetypes')
            return
        for ext, mimetype in custom_mimetypes.items():
            mimetypes.add_type(mimetype, ext)

    @property
    def _default_encoding(self):
        
        if cfg.opensesame_ide_use_system_default_encoding:
            return None
        return cfg.opensesame_ide_default_encoding

    def _selected_text(self, cursor):
        
        return textwrap.dedent(cursor.selectedText().replace(u'\u2029', u'\n'))
