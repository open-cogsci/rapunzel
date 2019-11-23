title: Download
next_title: Workflow
next_url: %url:workflow%


[TOC]


## Anaconda (cross-platform)

Rapunzel requires libraries from the `cogsci` and `conda-forge` channels. The recommended version of Python is 3.7.3.

```bash
conda config --add channels cogsci --add channels conda-forge
conda install rapunzel
conda install r-irkernel  # Optional: for R support
```

Once Rapunzel has been installed, you can start it from the Anaconda prompt (`rapunzel`) or the Anaconda navigator (after adding the `cogsci` channel).


## Windows

You can download a pre-built Windows package from [here](https://github.com/smathot/OpenSesame/releases). Extract the `zip` archive somewhere, and double-click on `rapunzel.bat` to start Rapunzel.


## Ubuntu

You can install Rapunzel through the `rapunzel` PPA:

```bash
sudo add-apt-repository ppa:smathot/rapunzel
sudo apt update
sudo apt install python3-rapunzel
```


## Source code

Rapunzel lives on GitHub:

- <https://github.com/smathot/rapunzel>
