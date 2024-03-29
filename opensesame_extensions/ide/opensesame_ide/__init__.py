"""Turn OpenSesame into an IDE"""

icon = "go-next"
aliases = ['OpenSesameIDE']
priority = 100
tooltip = "Turn OpenSesame into an IDE"
settings = {
    "opensesame_ide_last_folder": "",
    "opensesame_ide_pinned_files": "",
    "opensesame_ide_recent_folders": "",
    "opensesame_ide_run_autosave": False,
    "opensesame_ide_auto_tabs_to_spaces": False,
    "opensesame_ide_strip_lines": False,
    "opensesame_ide_show_tab_bar": True,
    "opensesame_ide_default_extension": ".py",
    "opensesame_ide_use_system_default_encoding": False,
    "opensesame_ide_default_encoding": "utf-8",
    "opensesame_ide_ignore_patterns": "*.pyc, *.pyo, *.coverage, .DS_Store, __pycache__, .git",
    "opensesame_ide_project_file": ".rapunzel.yaml",
    "opensesame_ide_max_index_files": 5000,
    "opensesame_ide_run_selection_change_working_directory": True,
    "opensesame_ide_shortcut_close_tab": "Ctrl+W",
    "opensesame_ide_shortcut_close_other_tabs": "Ctrl+Alt+W",
    "opensesame_ide_shortcut_close_all_tabs": "Ctrl+Shift+W",
    "opensesame_ide_shortcut_split_vertical": "Ctrl+Shift+V",
    "opensesame_ide_shortcut_split_horizontal": "Ctrl+Shift+H",
    "opensesame_ide_shortcut_switch_previous_panel": "Ctrl+Shift+[",
    "opensesame_ide_shortcut_switch_next_panel": "Ctrl+Shift+]",
    "opensesame_ide_shortcut_toggle_folder_browsers": "Ctrl+\\",
    "opensesame_ide_shortcut_locate_active_file": "Ctrl+Shift+\\",
    "opensesame_ide_shortcut_run_file": "F5",
    "opensesame_ide_shortcut_run_debug": "Ctrl+F5",
    "opensesame_ide_shortcut_toggle_breakpoint": "F12",
    "opensesame_ide_shortcut_clear_breakpoints": "Ctrl+F12",
    "opensesame_ide_shortcut_change_working_directory": "F8",
    "opensesame_ide_shortcut_run_selection": "F9",
    "opensesame_ide_shortcut_run_from_current_position": "Shift+F9",
    "opensesame_ide_shortcut_run_up_to_current_position": "Alt+F9",
    "opensesame_ide_shortcut_run_interrupt": "Ctrl+F9",
    "opensesame_ide_shortcut_toggle_fullscreen": "F11",
    "opensesame_ide_mimetypes": "{'.md': 'text/x-markdown', '.r': 'text/x-r', '.R': 'text/x-r'}"
}
modes = ["ide"]
