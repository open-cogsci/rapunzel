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
from libqtopensesame.misc.config import cfg
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
            ide.quick_select_files
        )
        self._action_open_folder = self._action(
            _(u'Open &folder…'),
            u'folder',
            u'Ctrl+Shift+O',
            ide.quick_select_folders
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
            u'window-close',
            u'Alt+F4',
            ide.main_window.close
        )
        self._menu_file = QMenu(_(u'&File'))
        self._menu_file.addAction(self._action_new_file)
        self._menu_file.addAction(self._action_open_file)
        self._menu_file.addAction(self._action_save_file)
        self._menu_file.addAction(self._action_save_file_as)
        self._menu_file.addAction(self._action_open_folder)
        if u'JupyterNotebook' in ide.extension_manager:
            jupyter_notebook = ide.extension_manager['JupyterNotebook']
            self._menu_file.addSeparator()
            self._menu_file.addAction(jupyter_notebook.action_import_ipynb)
            self._menu_file.addAction(jupyter_notebook.action_export_ipynb)
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
        self._action_jupyter_notebook = self._add_extension_action(
            'JupyterNotebook',
            menu=self._menu_tools
        )
        self.addMenu(self._menu_tools)
        # View menu
        self._action_close_tab = self._action(
            _(u'&Close tab'),
            u'window-close',
            cfg.opensesame_ide_shortcut_close_tab,
            ide.close_tab
        )
        self._action_close_other_tabs = self._action(
            _(u'Close &other tabs'),
            u'window-close',
            cfg.opensesame_ide_shortcut_close_other_tabs,
            ide.close_other_tabs
        )
        self._action_close_all_tabs = self._action(
            _(u'Close &all tabs'),
            u'window-close',
            cfg.opensesame_ide_shortcut_close_all_tabs,
            ide.close_all_tabs
        )
        self._action_split_vertical = self._action(
            _(u'Split &vertical'),
            u'go-down',
            cfg.opensesame_ide_shortcut_split_vertical,
            ide.split_vertical
        )
        self._action_split_horizontal = self._action(
            _(u'Split &horizontal'),
            u'go-next',
            cfg.opensesame_ide_shortcut_split_horizontal,
            ide.split_horizontal
        )
        self._action_switch_splitter_previous = self._action(
            _(u'Switch to previous panel'),
            u'go-previous',
            cfg.opensesame_ide_shortcut_switch_previous_panel,
            ide.switch_splitter_previous
        )
        self._action_switch_splitter_next = self._action(
            _(u'Switch to next panel'),
            u'go-next',
            cfg.opensesame_ide_shortcut_switch_next_panel,
            ide.switch_splitter_next
        )
        self._action_toggle_fullscreen = self._action(
            _(u'Toogle fullscreen'),
            u'view-fullscreen',
            cfg.opensesame_ide_shortcut_toggle_fullscreen,
            ide._toggle_fullscreen,
            checkable=True
        )
        self._action_toggle_folder_browsers = self._action(
            _(u'Toggle &folder browsers'),
            u'os-overview',
            cfg.opensesame_ide_shortcut_toggle_folder_browsers,
            ide.toggle_folder_browsers,
            checkable=True
        )
        self._action_locate_file_in_folder = self._action(
            _(u'&Locate active file'),
            u'folder',
            cfg.opensesame_ide_shortcut_locate_active_file,
            ide.locate_file_in_folder
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
        self._menu_view.addAction(self._action_toggle_fullscreen)
        self._menu_view.addSeparator()
        self._menu_view.addAction(self._action_toggle_folder_browsers)
        self._menu_view.addAction(self._action_locate_file_in_folder)
        self._action_toggle_console = self._add_extension_action(
            'JupyterConsole',
            menu=self._menu_view,
            separate=True
        )
        self._action_toggle_workspace = self._add_extension_action(
            'WorkspaceExplorer',
            menu=self._menu_view,
        )
        self._action_symbol_selector = self._add_extension_action(
            'SymbolSelector',
            menu=self._menu_view,
            separate=True
        )
        self._action_find_in_files = self._add_extension_action(
            'FindInFiles',
            menu=self._menu_view,
            separate=True
        )
        self._action_command_palette = self._add_extension_action(
            'CommandPalette',
            menu=self._menu_view,
            separate=True
        )
        self.addMenu(self._menu_view)
        # Run menu
        self._action_run_current_file = self._action(
            _(u'&Run project or file'),
            u'os-run',
            cfg.opensesame_ide_shortcut_run_file,
            ide.run_current_file,
        )
        self._action_run_current_selection = self._action(
            _(u'Run &selection, cell, or current line'),
            u'os-run-quick',
            cfg.opensesame_ide_shortcut_run_selection,
            ide.run_current_selection,
        )
        self._action_run_interrupt = self._action(
            _(u'&Interrupt kernel'),
            u'os-kill',
            cfg.opensesame_ide_shortcut_run_interrupt,
            ide.run_interrupt,
        )
        self._action_run_restart = self._action(
            _(u'Restart &kernel'),
            u'view-refresh',
            None,
            ide.run_restart,
        )
        self._action_change_working_directory = self._action(
            _(u'Change &working directory to active file'),
            u'folder-open',
            cfg.opensesame_ide_shortcut_change_working_directory,
            ide.change_working_directory,
        )
        self._menu_run = QMenu(_('&Run'))
        self._menu_run.addAction(self._action_run_current_file)
        self._menu_run.addAction(self._action_run_current_selection)
        self._menu_run.addSeparator()
        self._menu_run.addAction(self._action_run_interrupt)
        self._menu_run.addAction(self._action_run_restart)
        self._menu_run.addSeparator()
        self._menu_run.addAction(self._action_change_working_directory)
        self.addMenu(self._menu_run)

    def _add_extension_action(self, ext, menu, separate=False):

        if ext not in self._ide.extension_manager:
            return None
        if separate:
            menu.addSeparator()
        menu.addAction(self._ide.extension_manager[ext].action)
        return self._ide.extension_manager[ext].action

    def build_tool_bar(self):

        tool_bar = QToolBar(self.parent())
        tool_bar.setIconSize(QSize(32, 32))
        tool_bar.addAction(self._action_new_file)
        tool_bar.addAction(self._action_open_file)
        tool_bar.addAction(self._action_save_file)
        tool_bar.addAction(self._action_open_folder)
        tool_bar.addSeparator()
        tool_bar.addAction(self._action_run_current_file)
        tool_bar.addAction(self._action_run_current_selection)
        tool_bar.addAction(self._action_run_interrupt)
        tool_bar.addAction(self._action_run_restart)
        tool_bar.addSeparator()
        tool_bar.addAction(self._action_toggle_folder_browsers)
        if self._action_toggle_console is not None:
            tool_bar.addAction(self._action_toggle_console)
        if self._action_toggle_workspace is not None:
            tool_bar.addAction(self._action_toggle_workspace)
        if self._action_find_in_files is not None:
            tool_bar.addSeparator()
            tool_bar.addAction(self._action_find_in_files)
        tool_bar.setWindowTitle(u'IDE toolbar')
        tool_bar.setObjectName(u'OpenSesameIDE_Toolbar')
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
