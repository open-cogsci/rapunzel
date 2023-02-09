# Rapunzel

A modern code editor, focused on numerical computing with Python and R

Copyright 2019-2023 Sebastiaan Mathôt (@smathot)


## About

Rapunzel is a set of OpenSesame extensions that turn OpenSesame into an integrated development environment.

For documentation and installation instructions, see:

- <https://rapunzel.cogsci.nl/>

OpenSesame is hosted on GitHub:

- <https://github.com/smathot/OpenSesame/>


## List of extensions

- `opensesame_ide` is the main extension that contains most of the IDE functionality
- `find_in_files` implements the find-in-files functionality (`Ctrl+Shift+F`)
- `jupyter_notebook` provides export options to Notebook and other formats
- `workspace_explorer` provides the workspace explorer that allows inspection of variables for supported kernels
- `symbol_selector` provides the jump-to-symbol (functions, classes, etc.) functionality (`Ctrl+R`)
- `rapunzel_welcome` implements the welcome tab that is shown on startup
- `word_count` gives a notification with the number of words, lines, and characters of the current document
- `spell_check` implements the spell checker
- `data_viewer` allows supported file types to be imported into the kernel as objects
- `git_gui` opens Git GUI for the current document
- `rapunzel_locale` handles translations
- `python_debugger` implements the Rapunzel debugger for Python, based on the IPython debugger
- `image_annotations` captures images and text output inserts them as annotations or code comments into the document


## License

The Rapunzel icon is adapted from "Moka Icons" by Sam Hewitt, licensed under CC-SA-4.0.

- <https://github.com/snwh/moka-icon-theme>

The rest of Rapunzel is distributed under the terms of the GNU General Public License 3. The full license should be included in the file COPYING, or can be obtained from:

- <http://www.gnu.org/licenses/gpl.txt>
