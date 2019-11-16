title: Rapunzel


Rapunzel is under active development. Expect bugs!
{: .alert-info .alert}


Rapunzel is:

- A modern code editor
- Focused on numerical computing with Python and R
- Free and open-source
- Powered by [OpenSesame](https://osdoc.cogsci.nl/)


## Installation

### Anaconda (cross-platform)

Rapunzel requires libraries from the `cogsci` and `conda-forge` channels. The recommended version of Python is 3.7.3.

```
conda config --add channels cogsci --add channels conda-forge
conda install rapunzel
conda install r-irkernel  # Optional: for R support
```

Once Rapunzel has been installed, you can start it from the Anaconda prompt (`rapunzel`) or the Anaconda navigator.


### Windows

You can download a pre-built Windows package from [here](https://github.com/smathot/OpenSesame/releases/download/prerelease%2F3.3.0a31/opensesame_3.3.0a31_rapunzel_0.3.3-1.zip). Extract the `zip` archive somewhere, and double-click on `rapunzel.bat` to start Rapunzel.


### Ubuntu

You can install Rapunzel through the `rapunzel` PPA:

```
sudo add-apt-repository ppa:smathot/rapunzel
sudo apt update
sudo apt install python3-rapunzel
```


### Source code

Rapunzel lives on GitHub:

- <https://github.com/smathot/rapunzel>
