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
from qtpy.QtWidgets import QAction, QMenu, QMenuBar, QToolBar
from qtpy.QtCore import QSize
from libqtopensesame.misc.translate import translation_context
_ = translation_context(u'OpenSesameIDE', category=u'extension')


class MenuBar(QMenuBar):

    def __init__(self, parent, ide):

        super(MenuBar, self).__init__(parent)
        self._ide = ide
        # File menu
        self._action_new_file = self._action(
            _(u'&New'),
            u'document-new',
            u'Ctrl+N',
            ide.new_file
        )
        self._action_open_file = self._action(
            _(u'&Open…'),
            u'document-open',
            u'Ctrl+O',
            ide.open_file
        )
        self._action_open_folder = self._action(
            _(u'Open &folder…'),
            u'folder',
            u'Ctrl+Shift+O',
            ide.select_and_open_folder
        )
        self._action_save_file = self._action(
            _(u'&Save'),
            u'document-save',
            u'Ctrl+S',
            ide.save_file
        )
        self._action_save_file_as = self._action(
            _(u'Save &as…'),
            u'document-save-as',
            u'Ctrl+Shift+S',
            ide.save_file_as
        )
        self._action_quit = self._action(
            _(u'&Quit'),
            u'application-exit',
            u'Alt+F4',
            ide.main_window.close
        )
        self._menu_file = QMenu(_(u'&File'))
        self._menu_file.addAction(self._action_new_file)
        self._menu_file.addAction(self._action_open_file)
        self._menu_file.addAction(self._action_open_folder)
        self._menu_file.addAction(self._action_save_file)
        self._menu_file.addAction(self._action_save_file_as)
        self._menu_file.addSeparator()
        self._menu_file.addAction(self._action_quit)
        self.addMenu(self._menu_file)
        # Tools menu
        self._action_preferences = self._action(
            _(u'&Preferences'),
            u'preferences-system',
            None,
            ide.tabwidget.open_preferences
        )
        self._action_plugins = self._action(
            _(u'P&lugins'),
            u'preferences-system',
            None,
            ide.open_plugin_manager
        )
        self._menu_tools = QMenu(_(u'&Tools'))
        self._menu_tools.addAction(self._action_preferences)
        self._menu_tools.addAction(self._action_plugins)
        self.addMenu(self._menu_tools)
        # View menu
        self._action_close_tab = self._action(
            _(u'&Close tab'),
            u'window-close',
            u'Ctrl+W',
            ide.close_tab
        )
        self._action_close_other_tabs = self._action(
            _(u'Close &other tabs'),
            u'window-close',
            u'Ctrl+Alt+W',
            ide.close_other_tabs
        )
        self._action_close_all_tabs = self._action(
            _(u'Close &all tabs'),
            u'window-close',
            u'Ctrl+Shift+W',
            ide.close_all_tabs
        )
        self._action_split_vertical = self._action(
            _(u'Split &vertical'),
            u'go-down',
            u'Ctrl+Shift+V',
            ide.split_vertical
        )
        self._action_split_horizontal = self._action(
            _(u'Split &horizontal'),
            u'go-next',
            u'Ctrl+Shift+H',
            ide.split_horizontal
        )
        self._action_switch_splitter_previous = self._action(
            _(u'Switch to previous panel'),
            u'go-previous',
            u'Ctrl+Shift+[',
            ide.switch_splitter_previous
        )
        self._action_switch_splitter_next = self._action(
            _(u'Switch to next panel'),
            u'go-next',
            u'Ctrl+Shift+]',
            ide.switch_splitter_next
        )
        self._action_toggle_folder_browsers = self._action(
            _(u'Toggle &folder browsers'),
            u'folder',
            u'Ctrl+\\',
            ide.toggle_folder_browsers
        )
        self._action_locate_file_in_folder = self._action(
            _(u'&Locate active file'),
            u'folder',
            u'Ctrl+Shift+\\',
            ide.locate_file_in_folder
        )
        self._action_quick_select_files = self._action(
            _(u'F&ile selector'),
            u'document-open',
            u'Ctrl+P',
            ide.quick_select_files,
        )
        self._action_quick_select_symbols = self._action(
            _(u'S&ymbol selector'),
            u'text-x-script',
            u'Ctrl+R',
            ide.quick_select_symbols,
        )
        self._menu_view = QMenu(_('&View'))
        self._menu_view.addAction(self._action_close_tab)
        self._menu_view.addAction(self._action_close_other_tabs)
        self._menu_view.addAction(self._action_close_all_tabs)
        self._menu_view.addSeparator()
        self._menu_view.addAction(self._action_split_vertical)
        self._menu_view.addAction(self._action_split_horizontal)
        self._menu_view.addAction(self._action_switch_splitter_previous)
        self._menu_view.addAction(self._action_switch_splitter_next)
        self._menu_view.addSeparator()
        self._menu_view.addAction(self._action_toggle_folder_browsers)
        self._menu_view.addAction(self._action_locate_file_in_folder)
        try:
            self._action_toggle_console = \
                ide.extension_manager[u'JupyterConsole'].action
        except Exception:
            self._action_toggle_console = None
        else:
            self._menu_view.addSeparator()
            self._menu_view.addAction(self._action_toggle_console)
        self._menu_view.addSeparator()
        self._menu_view.addAction(self._action_quick_select_files)
        self._menu_view.addAction(self._action_quick_select_symbols)
        try:
            self._action_find_in_files = \
                ide.extension_manager[u'FindInFiles'].action
        except Exception:
            self._action_find_in_files = None
        else:
            self._menu_view.addSeparator()
            self._menu_view.addAction(self._action_find_in_files)
        self.addMenu(self._menu_view)
        # Run menu
        self._action_run_current_file = self._action(
            _(u'&Run current file'),
            u'os-run',
            u'F5',
            ide.run_current_file,
        )
        self._action_run_current_selection = self._action(
            _(u'Run &selection or current line'),
            u'os-run-quick',
            u'F9',
            ide.run_current_selection,
        )
        self._menu_run = QMenu(_('&Run'))
        self._menu_run.addAction(self._action_run_current_file)
        self._menu_run.addAction(self._action_run_current_selection)
        self.addMenu(self._menu_run)

    def build_tool_bar(self):

        tool_bar = QToolBar(self.parent())
        tool_bar.setIconSize(QSize(32, 32))
        tool_bar.addAction(self._action_new_file)
        tool_bar.addAction(self._action_open_file)
        tool_bar.addAction(self._action_open_folder)
        tool_bar.addAction(self._action_save_file)
        tool_bar.addSeparator()
        tool_bar.addAction(self._action_run_current_file)
        tool_bar.addAction(self._action_run_current_selection)
        if self._action_toggle_console is not None:
            tool_bar.addSeparator()
            tool_bar.addAction(self._action_toggle_console)
        if self._action_find_in_files is not None:
            tool_bar.addAction(self._action_find_in_files)
        tool_bar.setWindowTitle(u'IDE toolbar')
        return tool_bar

    def _action(self, title, icon, shortcut, target, checkable=False):

        action = QAction(title)
        action.setIcon(self._ide.theme.qicon(icon))
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(target)
        action.setCheckable(checkable)
        action.setPriority(QAction.HighPriority)
        return action
