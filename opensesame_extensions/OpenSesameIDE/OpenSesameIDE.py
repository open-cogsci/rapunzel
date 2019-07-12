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
from libopensesame.oslogging import oslogger
from libqtopensesame.extensions import BaseExtension
from libqtopensesame.misc.config import cfg
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QFileDialog
from opensesame_ide import FolderBrowserDockWidget, MenuBar
from libqtopensesame.misc.translate import translation_context
from pyqode.core.widgets import SplittableCodeEditTabWidget
from fallback_code_edit import FallbackCodeEdit
_ = translation_context(u'OpenSesameIDE', category=u'extension')


class OpenSesameIDE(BaseExtension):

    def event_startup(self):

        if u'--ide' not in sys.argv:
            return
        os.path.splitunc = lambda path: ('', path)  # Backwards compatibility
        self._scetw = SplittableCodeEditTabWidget(self.main_window)
        self._scetw.fallback_editor = FallbackCodeEdit
        self._scetw.tab_name = u'OpenSesameIDE'
        self._dock_widgets = {}
        self.tabwidget.add(
            self._scetw,
            u'accessories-text-editor',
            'IDE'
        )
        self._patch_behavior()
        if not os.path.isdir(cfg.opensesame_ide_last_folder):
            self._open_folder(os.getcwd())
        else:
            self._open_folder(cfg.opensesame_ide_last_folder)

    def open_document(self, path):

        editor = self._scetw.open_document(path)
        self.extension_manager.fire(
            u'register_editor',
            editor=editor
        )

    def remove_folder_browser_dock_widget(self, dock_widget):

        oslogger.info(u'removing folder browser: {}'.format(dock_widget.path))
        del self._dock_widgets[dock_widget.path]

    def close_tab(self):

        editor = self._scetw.current_widget()
        if editor is None:
            return
        tab_widget = editor.parent().parent()
        tab_widget.close()

    def split_horizontal(self):

        self._split(Qt.Horizontal)

    def split_vertical(self):

        self._split(Qt.Vertical)

    def select_and_open_folder(self):

        path = QFileDialog.getExistingDirectory(self.main_window)
        if isinstance(path, tuple):
            path = path[0]
        if path:
            self._open_folder(path)
            cfg.opensesame_ide_last_folder = path

    def new_file(self):

        self._scetw.create_new_document()

    def save_file(self):

        self._scetw.save_current()

    def save_file_as(self):

        self._scetw.save_current_as()

    def open_file(self):

        path = QFileDialog.getOpenFileName(
            self.main_window,
            _(u"Open file"),
            directory=cfg.file_dialog_path
        )
        if isinstance(path, tuple):
            path = path[0]
        if not path:
            return
        self.open_document(path)

    def toggle_folder_browsers(self):

        hidden = any(
            not dockwidget.isVisible()
            for dockwidget in self._dock_widgets.values()
        )
        oslogger.info('setting folder-browser visibility to {}'.format(hidden))
        for dockwidget in self._dock_widgets.values():
            dockwidget.visibilityChanged.disconnect()
            dockwidget.setVisible(hidden)
            dockwidget.visibilityChanged.connect(
                dockwidget.on_visibility_changed
            )

    def toggle_console(self):

        if not self._menubar._action_toggle_console.isChecked():
            self.main_window.ui.dock_stdout.setVisible(False)
            return
        self.main_window.ui.console.focus()
        self.main_window.ui.dock_stdout.setVisible(True)

    def quick_select_files(self):

        haystack = []
        for dock_widget in self._dock_widgets.values():
            for path in dock_widget.list_files():
                label = u'{}\n{}'.format(
                    os.path.basename(path),
                    path[len(dock_widget.path) + 1:]
                )
                data = path
                haystack.append((label, data, self.open_document))
        self.extension_manager.fire(u'quick_select', haystack=haystack)

    def _split(self, direction):

        editor = self._scetw.current_widget()
        if editor is None:
            return
        self._scetw.split(editor, direction)

    def _open_folder(self, path):

        if path in self._dock_widgets:
            return
        oslogger.info(u'adding folder browser: {}'.format(path))
        dock_widget = FolderBrowserDockWidget(self.main_window, self, path)
        self.main_window.addDockWidget(
            Qt.LeftDockWidgetArea,
            dock_widget
        )
        self._dock_widgets[path] = dock_widget

    def _patch_close_event(self, fnc):

        def inner(e):

            self._scetw.closeEvent(e)
            if e.isAccepted():
                fnc(e)

        return inner

    def _patch_behavior(self):

        self.tabwidget.switch(u'OpenSesameIDE')
        if not self.main_window.ui.action_onetabmode.isChecked():
            self.main_window.ui.action_onetabmode.trigger()
        self._menubar = MenuBar(self.main_window, self)
        self.main_window.setMenuBar(self._menubar)
        self.main_window.restore_window_state = \
            self._patch_restore_window_state(
                self.main_window.restore_window_state
            )
        self.main_window.closeEvent = self._patch_close_event(
            self.main_window.closeEvent
        )
        try:
            self.extension_manager['get_started'].activate = lambda: None
        except Exception:
            pass

    def _patch_restore_window_state(self, fnc):

        def inner():

            fnc()
            self.main_window.ui.toolbar_main.hide()
            self.main_window.ui.toolbar_items.hide()
            self.main_window.ui.dock_stdout.show()
            self.main_window.ui.dock_overview.hide()
            self.main_window.ui.dock_pool.hide()
            try:
                self.extension_manager['variable_inspector'].set_visible(False)
            except Exception:
                pass

        return inner
