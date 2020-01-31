title: Download
next_title: Workflow
next_url: %url:workflow%


[TOC]


## Anaconda (cross-platform)

Rapunzel requires libraries from the `cogsci` and `conda-forge` channels.

```bash
conda config --add channels cogsci --add channels conda-forge
conda install rapunzel
conda install r-irkernel  # Optional: for R support
```

Once Rapunzel has been installed, you can start it from the Anaconda prompt (`rapunzel`) or the Anaconda navigator (after adding the `cogsci` channel).


## Windows

Rapunzel is included with OpenSesame, and you can download a pre-built Windows packages from the OpenSesame download page:

- <https://osdoc.cogsci.nl/download>


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
