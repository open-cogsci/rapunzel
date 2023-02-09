"""A workspace explorer for Python kernels"""

label = "Show workspace"
tooltip = "Show Python workspace explorer"
icon = "os-inspector"
priority = 102
shortcut = "Ctrl+Shift+E"
modes = ["ide"]
settings = {
    "workspace_visible": False
}
checkable = True
menu = {
    "index": 8,
    "submenu": "View"
}
toolbar = {
    "index": 13
}
