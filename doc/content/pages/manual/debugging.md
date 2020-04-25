title: Debugging and exploring the workspace
next_title: Notebooks
next_url: %url:notebooks%


[TOC]


%--
video:
 source: youtube
 id: VidRapunzel
 videoid: t8wo4dTkUJA
 width: 640
 height: 360
 caption: |
  Visual debugging
--%


## Exploring the workspace


Press `ctrl+shift+e` to show/ hide the workspace explorer. This lists the global variables of the currenly active console (currently only for Python kernels). You can double-click on a variable to inspect it in more detail.


## Debugging


### Starting the debugger

Press `ctrl+F5` to run the current file in the debugger. (Currently, you can only run a full file in the debugger, and not a selection of code, a code cell, or a project file.) The Rapunzel debugger is built around [`ipdb`](https://ipython.readthedocs.io/en/stable/interactive/reference.html?highlight=ipdb#using-the-python-debugger-pdb), the IPython debugger.


### Debugger commands

At the debugger prompt (`ipdb>`), you can enter commands to control the debugging process. The most important commands are:

- `c` (`continue`) executes the program until a breakpoint is reached, an `Exception` occurs, or the program finishes successfully. This is generally the first thing you do after starting the debugger.
- `s` (`step`) executes the next line of code. If the next line of code is inside a function, this will take the debugger into the function.
- `n` (`next`) executes the next line of code of the current function. That is, unlike `step`, `next` does not take the debugger into function calls.
- `r` (`return`) executes until the current function returns.
- `u` (`up`) takes the debugger one level up in the call stack. That is, `up` allows you to inspect the state of the function from which the current function was called.
- `d` (`down`) takes the debugger one level down in the call stack. That is, it allows you to go back to the current function after having stepped `up` from it.

See the `pdb` manual for a full explanation of all commands:

- <https://docs.python.org/3/library/pdb.html#debugger-commands>


### Setting breakpoints

Press `F12` to set a breakpoint at the current line. This will cause the debugger to stop execution when this line is reached so that you can inspect the state of the code at that moment.

Press `ctrl+F12` to clear all breakpoints.


### Exploring the workspace while debugging

The workspace explorer also shows the state of the workspace while the debugger is active. However, currently you cannot inspect individual variables by double-clicking on them while te debugger is active.
