title: Download
next_title: Workflow
next_url: %url:workflow%


[TOC]


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


## Anaconda (cross-platform)

Rapunzel requires libraries from the `cogsci` and `conda-forge` channels.

```bash
conda config --add channels cogsci --add channels conda-forge
conda install rapunzel
conda install r-irkernel  # Optional: for R support
```

Once Rapunzel has been installed, you can start it from the Anaconda prompt (`rapunzel`) or the Anaconda navigator (after adding the `cogsci` channel).


## Windows

The standard download is based on Python 3.8 for 64 bit systems. The installer and `.zip` packages are identical, except for the installation.

<a role="button" class="btn btn-success btn-align-left" href="https://github.com/smathot/rapunzel/releases/download/release%2F0.4.7/rapunzel_0.4.7-py38-win64-2.exe">
	<b>Standard</b> Windows installer (.exe)
</a>

<a role="button" class="btn btn-default btn-align-left" href="https://github.com/smathot/rapunzel/releases/download/release%2F0.4.7/rapunzel_0.4.7-py38-win64-2.zip">
	<b>Standard</b> Windows no installation required (.zip)
</a>


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
