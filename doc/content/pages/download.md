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
conda install notebook pandoc  # Optional: for exporting/ importing to various formats
conda install opensesame-extension-language_server  # Optional: for language-server support
```

Once Rapunzel has been installed, you can start it from the Anaconda prompt (`rapunzel`) or the Anaconda navigator (after adding the `cogsci` channel).


## Windows

The standard download is a combined package that contains both OpenSesame and Rapunzel. It is based on Python 3.11 for 64 bit systems. The installer and `.zip` packages are identical, except for the installation.

<a role="button" class="btn btn-success btn-align-left" href="https://github.com/open-cogsci/OpenSesame/releases">
	<b>Standard</b> Windows installer (.exe)
</a>

<a role="button" class="btn btn-default btn-align-left" href="https://github.com/open-cogsci/OpenSesame/releases">
	<b>Standard</b> Windows no installation required (.zip)
</a>

## Mac OS

There are no Mac OS packages available at the moment. The recommended way to install Rapunzel on Mac OS is through [Anaconda](#anaconda-cross-platform).


## Ubuntu

You can install Rapunzel through the `cogscinl` (stable) or `milgram` (development) PPA:

```bash
sudo add-apt-repository ppa:smathot/cogscinl  # stable releases
sudo add-apt-repository ppa:smathot/milgram  # development releases
sudo apt update
sudo apt install python3-rapunzel python3-opensesame-extension-updater
sudo apt install jupyter-notebook jupyter-nbconvert pandoc  # Optional: for exporting/ importing to various formats
sudo apt install python3-opensesame-extension-language_server  # Optional: for language-server support
```

Alternatively you can install Rapunzel as a Snap package through the Ubuntu Software store or the command line:

```bash
sudo snap install rapunzel
```


## Source code

Rapunzel lives on GitHub:

- <https://github.com/smathot/rapunzel>


## Video: Installing in Anaconda

%--
video:
 source: youtube
 id: VidRapunzel
 videoid: ZPysys3Ew-w
 width: 640
 height: 360
 caption: |
  Installing Rapunzel in Anaconda
--%
