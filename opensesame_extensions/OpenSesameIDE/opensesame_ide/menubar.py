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
from qtpy.QtWidgets import QAction, QMenu, QMenuBar, QToolBar
from qtpy.QtCore import QSize
from libqtopensesame.misc.config import cfg
from libqtopensesame.misc.translate import translation_context
_ = translation_context(u'OpenSesameIDE', category=u'extension')


class MenuBar(QMenuBar):

    def __init__(self, parent, ide):

        super(MenuBar, self).__init__(parent)
        self._ide = ide
        self._cfg_actions = {}
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
        self._action_close_all_folders = self._action(
            _(u'&Close all folders'),
            u'folder',
            None,
            ide.close_all_folders
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
        self._menu_file = self.addMenu(_(u'&File'))
        self._menu_file.addAction(self._action_new_file)
        self._menu_file.addAction(self._action_open_file)
        self._menu_file.addAction(self._action_save_file)
        self._menu_file.addAction(self._action_save_file_as)
        self._menu_file.addAction(self._action_open_folder)
        self._menu_file.addSeparator()
        self._menu_file.addAction(self._action_close_all_folders)
        self._menu_file.addSeparator()
        self._menu_file.addAction(self._action_quit)
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
        self._menu_tools = self.addMenu(_(u'&Tools'))
        self._menu_tools.addAction(self._action_preferences)
        self._menu_tools.addAction(self._action_plugins)
        self._menu_tools.addSeparator()
        self._action_jupyter_notebook = self._add_extension_action(
            'JupyterNotebook',
            menu=self._menu_tools
        )
        self._action_git_gui = self._add_extension_action(
            'GitGUI',
            menu=self._menu_tools
        )
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
            _(u'Toggle fullscreen'),
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
        self._menu_view = self.addMenu(_('&View'))
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
        # Run menu
        self._menu_run = self.addMenu(_('&Run'))
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
        self._action_run_from_current_position = self._action(
            _(u'Run &from current position'),
            u'os-run-quick',
            cfg.opensesame_ide_shortcut_run_from_current_position,
            ide.run_from_current_position,
        )
        self._action_run_up_to_current_position = self._action(
            _(u'Run &up to current position'),
            u'os-run-quick',
            cfg.opensesame_ide_shortcut_run_up_to_current_position,
            ide.run_up_to_current_position,
        )
        self._action_capture_output = self._cfg_action(
            self._menu_run,
            _(u'&Capture output'),
            u'image_annotations_capture_output'
        )
        self._action_run_debug = self._action(
            _(u'Run file in &debugger'),
            u'os-run',
            cfg.opensesame_ide_shortcut_run_debug,
            ide.run_debug,
        )
        self._action_toggle_breakpoint = self._action(
            _(u'&Toggle breakpoint'),
            u'list-add',
            cfg.opensesame_ide_shortcut_toggle_breakpoint,
            ide.toggle_breakpoint,
        )
        self._action_clear_breakpoints = self._action(
            _(u'Clear &breakpoints'),
            u'list-remove',
            cfg.opensesame_ide_shortcut_clear_breakpoints,
            ide.clear_breakpoints,
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
        # Run menu
        self._menu_run.addAction(self._action_run_current_file)
        self._menu_run.addAction(self._action_run_current_selection)
        self._menu_run.addAction(self._action_run_from_current_position)
        self._menu_run.addAction(self._action_run_up_to_current_position)
        self._menu_run.addSeparator()
        self._menu_run.addAction(self._action_capture_output)
        self._menu_run.addSeparator()
        self._menu_run.addAction(self._action_run_interrupt)
        self._menu_run.addAction(self._action_run_restart)
        self._menu_run.addSeparator()
        self._menu_run.addAction(self._action_change_working_directory)
        self._menu_run.addSeparator()
        self._menu_run.addAction(self._action_run_debug)
        self._menu_run.addAction(self._action_toggle_breakpoint)
        self._menu_run.addAction(self._action_clear_breakpoints)
        # Editor menu
        self._menu_editor = self.addMenu(_('&Editor'))
        self._action_toggle_line_wrap = self._cfg_action(
            self._menu_editor,
            _(u'Wrap lines'),
            u'pyqode_line_wrap'
        )
        self._action_toggle_whitespaces = self._cfg_action(
            self._menu_editor,
            _(u'Show whitespace'),
            u'pyqode_show_whitespaces'
        )
        self._action_toggle_line_numbers = self._cfg_action(
            self._menu_editor,
            _(u'Show line numbers'),
            u'pyqode_show_line_numbers'
        )
        self._action_toggle_tab_bar = self._action(
            _(u'Show editor tabs'),
            None,
            None,
            self._toggle_show_tab_bar,
            checkable=True,
            checked=cfg.opensesame_ide_show_tab_bar
        )
        self._action_select_indentation_mode = self._action(
            _(u'Select indentation mode'),
            u'accessories-text-editor',
            None,
            self._select_indentation_mode
        )
        self._action_toggle_code_folding = self._cfg_action(
            self._menu_editor,
            _(u'Code folding'),
            u'pyqode_code_folding'
        )
        self._action_toggle_right_margin = self._cfg_action(
            self._menu_editor,
            _(u'Show right margin'),
            u'pyqode_right_margin'
        )
        self._action_toggle_fixed_width = self._cfg_action(
            self._menu_editor,
            _(u'Fixed editor width'),
            u'pyqode_fixed_width'
        )
        self._action_toggle_code_completion = self._cfg_action(
            self._menu_editor,
            _(u'Code completion'),
            u'pyqode_code_completion'
        )
        self._menu_editor.addAction(self._action_toggle_tab_bar)
        self._menu_editor.addAction(self._action_select_indentation_mode)
        self._action_word_count = self._add_extension_action(
            'SpellCheck',
            menu=self._menu_editor,
            separate=True
        )
        self._action_word_count = self._add_extension_action(
            'WordCount',
            menu=self._menu_editor,
            separate=True
        )

    def _add_extension_action(self, ext, menu, separate=False):

        if ext not in self._ide.extension_manager:
            return None
        if separate:
            menu.addSeparator()
        menu.addAction(self._ide.extension_manager[ext].action)
        return self._ide.extension_manager[ext].action

    def build_tool_bar(self):

        tool_bar = ToolBar(self.parent(), self._ide)
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
    
    def setting_changed(self, setting, value):
        
        if setting in self._cfg_actions:
            self._cfg_actions[setting].setChecked(value)
    
    def _cfg_action(
        self,
        menu,
        title,
        setting,
        icon=None,
        shortcut=None
    ):

        action = QAction(title, self)
        if icon:
            action.setIcon(self._ide.theme.qicon(icon))
        if shortcut:
            action.setShortcut(shortcut)
            action.setToolTip(
                u'{} ({})'.format(title.replace(u'&', u''), shortcut)
            )
        
        def change_setting(value):
            self._ide.extension_manager.fire(
                'setting_changed',
                setting=setting,
                value=value
            )
            
        action.triggered.connect(change_setting)
        action.setCheckable(True)
        action.setChecked(cfg[setting])
        action.setPriority(QAction.HighPriority)
        menu.addAction(action)
        self._cfg_actions[setting] = action
        return action

    def _action(
        self,
        title,
        icon,
        shortcut,
        target,
        checkable=False,
        checked=False
    ):

        action = QAction(title, self)
        if icon:
            action.setIcon(self._ide.theme.qicon(icon))
        if shortcut:
            action.setShortcut(shortcut)
            action.setToolTip(
                u'{} ({})'.format(title.replace(u'&', u''), shortcut)
            )
        action.triggered.connect(target)
        if checkable:
            action.setCheckable(True)
            action.setChecked(checked)
        action.setPriority(QAction.HighPriority)
        return action

    def _toggle_show_tab_bar(self, show_tab_bar):

        self._ide.extension_manager.fire(
            'ide_show_tab_bar',
            show_tab_bar=show_tab_bar
        )

    def _select_indentation_mode(self):

        self._ide.extension_manager.fire('pyqode_select_indentation_mode')


class ToolBar(QToolBar):

    def __init__(self, parent, ide):

        super(QToolBar, self).__init__(parent)
        self._ide = ide
        self.setIconSize(QSize(32, 32))
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):

        m = e.mimeData()
        if m.hasUrls() and all(url.isLocalFile() for url in m.urls()):
            e.acceptProposedAction()

    def dropEvent(self, e):

        m = e.mimeData()
        if m.hasUrls() and all(url.isLocalFile() for url in m.urls()):
            for url in m.urls():
                path = url.path()
                # On Windows, Qt for some reasons prefixes a slash to the path
                # like so: /c:/folder/file. We strip this.
                if path.startswith(u'/') and os.path.exists(path[1:]):
                    path = path[1:]
                if os.path.isdir(path):
                    self._ide._open_folder(path)
                else:
                    self._ide.open_document(path)
