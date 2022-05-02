# Rapunzel

A modern code editor, focused on numerical computing with Python and R

Copyright 2019-2022 Sebastiaan Mathôt (@smathot)


## About

Rapunzel is a set of OpenSesame extensions that turn OpenSesame into an integrated development environment.

For documentation and installation instructions, see:

- <https://rapunzel.cogsci.nl/>

OpenSesame is hosted on GitHub:

- <https://github.com/smathot/OpenSesame/>


## List of extensions

- `OpenSesameIDE` is the main extension that contains most of the IDE functionality
- `FindInFiles` implements the find-in-files functionality (`Ctrl+Shift+F`)
- `JupyterConsole` implements the Jupyter Console
- `JupyterNotebook` provides export options to Notebook and other formats
- `QuickSelector` provides the general quick-switching framework, which is used by other extensions
- `WorkspaceExplorer` provides the workspace explorer that allows inspection of variables for supported kernels
- `SymbolSelector` provides the jump-to-symbol (functions, classes, etc.) functionality (`Ctrl+R`)
- `RapunzelWelcome` implements the welcome tab that is shown on startup
- `CommandPalette` provides access to all menu options through a quick switcher
- `WordCount` gives a notification with the number of words, lines, and characters of the current document
- `SpellCheck` implements the spell checker
- `DataViewer` allows supported file types to be imported into the kernel as objects
- `GitGUI` opens Git GUI for the current document
- `RapunzelLocale` handles translations
- `PythonDebugger` implements the Rapunzel debugger for Python, based on the IPython debugger
- `SubprocessManager` keeps track of all subprocess that were launched by Rapunzel
- `ImageAnnotations` captures images and text output inserts them as annotations or code comments into the document


## License

The Rapunzel icon is adapted from "Moka Icons" by Sam Hewitt, licensed under CC-SA-4.0.

- <https://github.com/snwh/moka-icon-theme>

The rest of Rapunzel is distributed under the terms of the GNU General Public License 3. The full license should be included in the file COPYING, or can be obtained from:

- <http://www.gnu.org/licenses/gpl.txt>
