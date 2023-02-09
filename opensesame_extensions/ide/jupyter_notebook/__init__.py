"""Import and export Jupyter Notebook (.ipynb) files"""

label = "Launch Jupyter Lab"
tooltip = "Import and export Jupyter Notebook (.ipynb) files"
priority = 101
modes = ["ide"]
menu = {
    "index": -1,
    "separator_after": False,
    "separator_before": True,
    "submenu": "Tools"
}
settings = {
    "jupyter_lab_executable": "",
    "jupyter_lab_args": ""
}
