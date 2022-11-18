title: Installing packages, plugins, and extensions


If you receive permission errors on Windows, run OpenSesame / Rapunzel as administrator or pass the <code>--user</code> flag to pip.
{: .alert .alert-info}


[TOC]


## Package managers

### Conda

The standard Windows packages of OpenSesame / Rapuzel come with a fully functioning Anaconda environment. This means that you can use `conda` to manage packages.

Example: To install `seaborn` (a plotting library) execute the following command in the console:

```bash
conda install seaborn -y
```

*Example:* to update `rapunzel` and all its dependencies (which includes OpenSesame) using the `cogsci` and `conda-forge` channels:

```bash
conda update rapunzel -c cogsci -c conda-forge -y
```

Pro-tips:

- Pass the `-y` flag to avoid `conda` from prompting for input, which sometimes freezes the console.
- Have patience! `conda` is known to be slow, and you will not get visual feedback until the command is finished.
- In some cases, you may need to prefix the `conda` command with `!` to indicate that you want to execute a program rather than Python code.

The official `conda` docs:

- <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-pkgs.html>


### Pip

You can use `pip` to manage packages directly from the console. Prefix `pip` with `!` (to indicate that you want to execute a program rather than Python code).

Example: To install the OpenScienceFramework extension enter the following command into the console:

```bash
pip install opensesame-extension-osf
```

Pro-tips:

- The `--user` flag allows you to install libraries without requiring administrator privileges.
- In some cases, you may need to prefix the `pip` command with `!` to indicate that you want to execute a program rather than Python code.

The official `pip` docs:

- <https://pip.pypa.io/en/stable/user_guide/>


## Customizing your environment

### Using an environment file

You can tell OpenSesame / Rapunzel to scan extra folders, by specifying these folders in a file called `environment.yaml`. There are three entries:

- `PYTHON_PATH` is a semicolon-separated list of folders that are scanned for Python packages.
- `OPENSESAME_PLUGIN_PATH` is a semicolon-separated list of folders that are scanned for OpenSesame / Rapunzel extensions.
- `OPENSESAME_EXTENSION_PATH` is a semi-colon separated list of folders that are scanned for OpenSesame plugins (not used in Rapunel).

Each entry should be a semicolon-separated list of folders. All entries are optional and are prepended to the folders that are already scanned.

```yaml
PYTHON_PATH: "/home/user/mylibs1;/home/user/mylibs2"
OPENSESAME_PLUGIN_PATH: "/home/user/myplugins1;/home/user/myplugins2"
OPENSESAME_EXTENSION_PATH: "/home/user/myextensions1;/home/user/myextensions2"
```

This file should be placed in the working directory of OpenSesame. Under Windows, this is generally the OpenSesame program folder; under Linux and Mac OS this is generally your home folder. You can find out what the working directory is by executing the following in the debug window:

```python
import os
print(os.getcwd())
```


### Using environment variables

The following environment variables control your Python environment:

- `PYTHON_PATH` is a colon-separated list of folders that are scanned for Python packages. (See [official Python docs](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH).)
- `OPENSESAME_EXTENSION_PATH` is a semicolon-separated list of folders that are scanned for OpenSesame / Rapunzel extensions.
- `OPENSESAME_PLUGIN_PATH` is a semi-colon separated list of folders that are scanned for OpenSesame plugins (not used in Rapunel).
- `OPENSESAME_RESOURCES_PATH` is a single additional folder to scan for resource files (e.g. locale and ui files). This is mostly for development or packaging purposes.
