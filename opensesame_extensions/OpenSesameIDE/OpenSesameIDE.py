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
from libopensesame import metadata
from libopensesame.oslogging import oslogger
from libqtopensesame.extensions import BaseExtension
from libqtopensesame.misc.config import cfg
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QFileDialog, QMessageBox, QPushButton
from opensesame_ide import FolderBrowserDockWidget, MenuBar
from libqtopensesame.misc.translate import translation_context
from pyqode.core import widgets
from pyqode_extras.widgets import FallbackCodeEdit
_ = translation_context(u'OpenSesameIDE', category=u'extension')


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
        self._add_ide_tab()
        self._dock_widgets = {}
        self._set_ignore_patterns()
        self._restore_open_folders()
        self._parse_command_line()
        self.main_window.setWindowTitle(u'Rapunzel')
        self.main_window.setWindowIcon(
            self.theme.qicon(u'rapunzel')
        )

    def event_setting_changed(self, setting, value):
        
        self.extension_manager.suspend()
        self._menubar.setting_changed(setting, value)
        self.extension_manager.resume()

    def event_ide_open_file(self, path, line_number=1):

        self.open_document(path)
        self.extension_manager.fire('ide_jump_to_line', lineno=line_number)

    def event_ide_show_tab_bar(self, show_tab_bar):

        cfg.opensesame_ide_show_tab_bar = show_tab_bar
        self._scetw.tab_bar_visible = show_tab_bar

    def event_ide_new_file(self, source=None):

        self.new_file()
        if source is None:
            return
        self._current_editor().setPlainText(source)

    def event_ide_run_current_file(self):

        self.run_current_file()

    def event_ide_run_current_selection(self):

        self.run_current_selection()

    def provide_ide_current_source(self):

        editor = self._current_editor()
        if editor is None:
            return u''
        return editor.toPlainText()

    def provide_ide_current_language(self):

        editor = self._current_editor()
        if editor is None:
            return None
        return editor.language

    def open_document(self, path):

        # First normalize the path and check if there's a custom handler for it
        path = os.path.abspath(os.path.normcase(path))
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
            if path == os.path.normpath(os.path.normcase(editor.file.path)):
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
            clean_trailing_whitespaces=cfg.opensesame_ide_strip_lines
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

        tab_widget = self._current_tabwidget()
        if tab_widget is not None:
            tab_widget.close()

    def close_all_tabs(self):

        tab_widget = self._current_tabwidget()
        if tab_widget is not None:
            tab_widget.close_all()

    def close_other_tabs(self):

        tab_widget = self._current_tabwidget()
        if tab_widget is not None:
            tab_widget.close_others()

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

    def new_file(self):

        editor = self._current_splitter().create_new_document(
            extension=cfg.opensesame_ide_default_extension
        )
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

    def save_file_as(self):

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
            for dockwidget in self._dock_widgets.values()
        )

    def toggle_folder_browsers(self):

        hidden = not self.folder_browsers_visible()
        oslogger.debug(
            'setting folder-browser visibility to {}'.format(hidden)
        )
        for dockwidget in self._dock_widgets.values():
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

    def run_current_file(self):

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
        self.extension_manager.fire(u'jupyter_run_file', path=editor.file.path)

    def change_working_directory(self):

        path = self._current_path()
        if not os.path.isfile(path):
            return
        self.extension_manager.fire(
            u'jupyter_change_dir',
            path=os.path.dirname(path)
        )

    def run_current_selection(self):

        # 1. If text is selected, run the selected text
        # 2. Else, if the cursor is in a notebook cell, select and run the
        #    cell.
        # 3. Else, select and run the current line
        editor = self._current_editor()
        if editor is None:
            return
        # If the current editor is attached to a file, change the working
        # directory if this behavior is specified in the configuration
        if cfg.opensesame_ide_run_selection_change_working_directory:
            self.change_working_directory()
        cursor = editor.textCursor()
        if not cursor.hasSelection():
            cells = self.extension_manager.provide(
                u'jupyter_notebook_cells',
                code=editor.toPlainText(),
                cell_types=[u'code']
            )
            if cells is None:
                cells = []
            for cell in cells:
                if cell['start'] <= cursor.position() <= cell['end']:
                    # Select code cell
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
        code = textwrap.dedent(cursor.selectedText().replace(u'\u2029', u'\n'))
        self.extension_manager.fire(u'jupyter_run_code', code=code)

    def run_interrupt(self):

        self.extension_manager.fire(u'jupyter_interrupt')

    def run_restart(self):

        self.extension_manager.fire(u'jupyter_restart')

    def open_plugin_manager(self):

        self.extension_manager.activate(u'plugin_manager')

    def event_ide_jump_to_line(self, lineno):

        editor = self._scetw.current_widget()
        if not editor:
            return
        lines = editor.toPlainText().split(u'\n')
        position = sum([len(line) for line in lines[:lineno - 1]]) + lineno - 1
        cursor = editor.textCursor()
        cursor.setPosition(position)
        editor.setTextCursor(cursor)

    def quick_select_files(self):

        haystack = []
        for dock_widget in self._dock_widgets.values():
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
        for path in cfg.opensesame_ide_recent_folders.split(u';'):
            if not os.path.isdir(path):
                continue
            haystack.append((path, path, self._open_folder))
        self.extension_manager.fire(
            u'quick_select',
            haystack=haystack,
            placeholder_text=_(u'Search recent folders or browse disk …'),
            default=(_(u'Browse disk …'), None, self.select_and_open_folder)
        )

    def project_files(self, extra_ignore_pattern=None):

        for dock_widget in self._dock_widgets.values():
            for path in dock_widget.file_list:
                yield path
                
    def settings_widget(self):
        
        from opensesame_ide import Preferences
        return Preferences(self.main_window)

    def _split(self, direction):

        editor = self._current_editor()
        if editor is None:
            return
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
        splitter.main_tab_widget.close()
        for index in range(splitter.main_tab_widget.count()):
            editor = splitter.main_tab_widget.widget(index)
            if editor is None:  # This seems to happen under race conditions
                continue
            subsplitter.main_tab_widget._on_tab_move_request(editor, index)
        subsplitter.main_tab_widget.setCurrentIndex(
            subsplitter.main_tab_widget.count() - 1
        )
        self.main_window.setUpdatesEnabled(True)

    def _open_folder(self, path):

        path = os.path.abspath(path)
        if path in self._dock_widgets:
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

        for dockwidget in list(self._dock_widgets.values()):
            dockwidget.close()

    def locate_file_in_folder(self):

        for dockwidget in self._dock_widgets.values():
            dockwidget.setVisible(True)
        editor = self._current_editor()
        if editor is None:
            return
        for dock_widget in self._dock_widgets.values():
            dock_widget.select_path(editor.file.path)
        if not self.folder_browsers_visible():
            self.toggle_folder_browsers()

    def _patch_close_event(self, fnc):

        def inner(e):

            self.main_window.setUpdatesEnabled(False)
            self._scetw.closeEvent(e)
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
        self.tabwidget.tabCloseRequested.connect(self._on_tabwidget_close)
        self.tabwidget.shortcut_switch_left.setKey(u'')
        self.tabwidget.shortcut_switch_right.setKey(u'')
        # Create a custom menubar
        self._menubar = MenuBar(self.main_window, self)
        self.main_window.setMenuBar(self._menubar)
        self._toolbar = self._menubar.build_tool_bar()
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
            for dockwidget in self._dock_widgets.values():
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

        folders = [d.path for d in self._dock_widgets.values()]
        cfg.opensesame_ide_last_folder = u';'.join(folders)

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

    def _parse_command_line(self):

        for arg in sys.argv[1:]:
            if os.path.isfile(arg):
                self.open_document(arg)
            elif os.path.isdir(arg):
                self._open_folder(arg)

    def _current_project_file(self):

        editor = self._current_editor()
        if editor is None:
            return None
        for d in self._dock_widgets.values():
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

        return self._scetw.current_widget()

    def _current_original_editor(self):

        editor = self._scetw.current_widget()
        if editor is None:
            return
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

    def _current_tabwidget(self):

        editor = self._current_editor()
        if editor is None or editor.parent() is None:
            return
        return editor.parent().parent()

    def _current_splitter(self):

        editor = self._current_editor()
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
