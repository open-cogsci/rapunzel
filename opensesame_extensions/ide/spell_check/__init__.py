"""Provides a spell checker"""


label = "Check spelling"
tooltip = "Check spelling"
shortcut = "Ctrl+Alt+S"
icon = "edit-flag"
priority = -2
menu = {
    "index": 3,
    "submenu": "View"
}
settings = {
    "spellcheck_default_language": "en",
    "spellcheck_mimetypes": "markdown",
    "spellcheck_ignore": ""
}
modes = ["ide"]
