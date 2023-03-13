"""Adds a button and menu item to launch Rapunzel code editor"""

label = "Rapunzel Code Editor"
description = "Launches Code Editor"
aliases = ['IDELauncher']
modes = ["default"]
tooltip = "Launch Code Editor"
icon = "rapunzel"
priority = -2
settings = {
    "ide_executable": ""
}
menu = {
    "index": -7,
    "submenu": "Tools"
}
